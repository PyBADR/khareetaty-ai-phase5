import psycopg2
import pandas as pd
from prophet import Prophet
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

DB_CONN = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME", "khareetaty_ai"),
    "user": os.getenv("DB_USER", "bdr.ai"),
    "password": os.getenv("DB_PASSWORD", "")
}

def predict_trends():
    """Generate crime trend forecasts using Prophet"""
    try:
        conn = psycopg2.connect(**DB_CONN)
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        raise

    # Get daily incident counts for time series analysis
    df = pd.read_sql("""
        SELECT timestamp::date as ds, COUNT(*) as y
        FROM incidents_clean
        WHERE timestamp >= NOW() - INTERVAL '90 days'
        GROUP BY ds ORDER BY ds ASC
    """, conn)

    if len(df) < 3:
        logger.warning("Not enough data for forecast.")
        return

    # Prophet requires 'ds' and 'y' column names
    df.rename(columns={"ds": "ds", "y": "y"}, inplace=True)
    df['ds'] = pd.to_datetime(df['ds'])

    # Fit Prophet model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        interval_width=0.95
    )
    model.fit(df)
    
    # Create future dataframe for 7-day forecast
    future = model.make_future_dataframe(periods=7)
    forecast = model.predict(future)

    cur = conn.cursor()
    # Insert forecasted values for the next 7 days
    for _, row in forecast.tail(7).iterrows():
        cur.execute("""
            INSERT INTO zones_hotspots (zone, score, predicted, created_at)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (zone, predicted) DO UPDATE SET
                score = EXCLUDED.score,
                created_at = EXCLUDED.created_at
        """,
        ("kuwait_total_forecast", float(row["yhat"]), True, datetime.now()))

    conn.commit()
    conn.close()
    logger.info("Forecasting complete. Added 7-day predictions to zones_hotspots.")


def predict_by_zone(zone_type='district', forecast_hours=24):
    """
    Generate 24-hour forecasts per zone (district or police_zone)
    
    Args:
        zone_type: 'district' or 'police_zone'
        forecast_hours: Number of hours to forecast (default 24)
    
    Returns:
        Number of zones processed
    """
    try:
        conn = psycopg2.connect(**DB_CONN)
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        raise
    
    cur = conn.cursor()
    
    # Get zones with sufficient data
    zones_df = pd.read_sql(f"""
        SELECT DISTINCT {zone_type}
        FROM incidents_clean
        WHERE {zone_type} IS NOT NULL
        AND timestamp >= NOW() - INTERVAL '90 days'
    """, conn)
    
    if zones_df.empty:
        logger.warning(f"No {zone_type}s found with incidents")
        conn.close()
        return 0
    
    zones = zones_df[zone_type].tolist()
    logger.info(f"Generating {forecast_hours}h forecasts for {len(zones)} {zone_type}s")
    
    processed_count = 0
    
    for zone in zones:
        try:
            # Get hourly incident counts for this zone
            df = pd.read_sql(f"""
                SELECT 
                    DATE_TRUNC('hour', timestamp) as ds,
                    COUNT(*) as y
                FROM incidents_clean
                WHERE {zone_type} = %s
                AND timestamp >= NOW() - INTERVAL '90 days'
                GROUP BY ds
                ORDER BY ds ASC
            """, conn, params=(zone,))
            
            if len(df) < 24:  # Need at least 24 hours of data
                logger.debug(f"{zone_type} {zone}: Insufficient data ({len(df)} hours)")
                continue
            
            df['ds'] = pd.to_datetime(df['ds'])
            
            # Simple moving average forecast (faster than Prophet for hourly data)
            recent_avg = df.tail(24)['y'].mean()
            recent_trend = df.tail(48)['y'].mean() - df.tail(96).head(48)['y'].mean()
            
            # Predict next 24h with trend adjustment
            predicted_count = max(0, int(recent_avg + (recent_trend * 0.5)))
            
            # Calculate week-over-week change
            week_ago_avg = df[df['ds'] >= (datetime.now() - timedelta(days=7))]['y'].mean()
            if week_ago_avg > 0:
                pct_change = ((recent_avg - week_ago_avg) / week_ago_avg) * 100
            else:
                pct_change = 0
            
            # Get police zone for this district
            police_zone = None
            if zone_type == 'district':
                pz_result = pd.read_sql(
                    "SELECT police_zone FROM incidents_clean WHERE district = %s LIMIT 1",
                    conn, params=(zone,)
                )
                if not pz_result.empty:
                    police_zone = pz_result.iloc[0]['police_zone']
            else:
                police_zone = zone
            
            # Insert forecast
            cur.execute("""
                INSERT INTO zones_hotspots 
                (zone, score, predicted, zone_type, district, police_zone, 
                 forecast_count, forecast_timestamp, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (zone, predicted) DO UPDATE SET
                    score = EXCLUDED.score,
                    forecast_count = EXCLUDED.forecast_count,
                    forecast_timestamp = EXCLUDED.forecast_timestamp,
                    created_at = EXCLUDED.created_at
            """, (
                f"{zone}_forecast_{forecast_hours}h",
                pct_change,  # Store trend as score
                True,  # predicted = True
                f'{zone_type}_forecast',
                zone if zone_type == 'district' else None,
                police_zone,
                predicted_count,
                datetime.now() + timedelta(hours=forecast_hours),
                datetime.now()
            ))
            
            processed_count += 1
            logger.debug(f"{zone}: Forecast {predicted_count} incidents in next {forecast_hours}h (trend: {pct_change:+.1f}%)")
            
        except Exception as e:
            logger.error(f"Error forecasting for {zone_type} {zone}: {e}")
            continue
    
    conn.commit()
    conn.close()
    logger.info(f"Zone forecasting complete. Processed {processed_count}/{len(zones)} {zone_type}s.")
    return processed_count

def predict_by_governorate():
    """Generate forecasts by governorate"""
    try:
        conn = psycopg2.connect(**DB_CONN)
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        raise

    # Get list of governorates
    gov_df = pd.read_sql("SELECT DISTINCT governorate FROM incidents_clean WHERE governorate IS NOT NULL", conn)
    
    for _, row in gov_df.iterrows():
        gov = row['governorate']
        
        # Get daily incident counts for this governorate
        query = """
            SELECT timestamp::date as ds, COUNT(*) as y
            FROM incidents_clean
            WHERE governorate = %s AND timestamp >= NOW() - INTERVAL '90 days'
            GROUP BY ds ORDER BY ds ASC
        """
        df = pd.read_sql(query, conn, params=(gov,))

        if len(df) < 3:
            logger.warning(f"Not enough data for forecast in {gov}.")
            continue

        # Prophet requires 'ds' and 'y' column names
        df.rename(columns={"ds": "ds", "y": "y"}, inplace=True)
        df['ds'] = pd.to_datetime(df['ds'])

        # Fit Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            interval_width=0.95
        )
        model.fit(df)
        
        # Create future dataframe for 7-day forecast
        future = model.make_future_dataframe(periods=7)
        forecast = model.predict(future)

        cur = conn.cursor()
        # Insert forecasted values for the next 7 days
        for _, row in forecast.tail(7).iterrows():
            cur.execute("""
                INSERT INTO zones_hotspots (zone, score, predicted, created_at)
                VALUES (%s,%s,%s,%s)
                ON CONFLICT (zone, predicted) DO UPDATE SET
                    score = EXCLUDED.score,
                    created_at = EXCLUDED.created_at
            """,
            (f"{gov}_forecast", float(row["yhat"]), True, datetime.now()))

    conn.commit()
    conn.close()
    logger.info("Governorate forecasting complete.")


if __name__ == "__main__":
    predict_trends()
    predict_by_governorate()