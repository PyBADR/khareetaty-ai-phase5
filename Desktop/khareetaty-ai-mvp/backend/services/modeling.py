"""Predictive modeling service for trend forecasting"""
import psycopg2
import os
from datetime import datetime, timedelta
import json

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "khareetaty_ai"),
        user=os.getenv("DB_USER", "bdr.ai"),
        password=os.getenv("DB_PASSWORD", "secret123"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )

def predict_trends():
    """Predict crime trends using historical data"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Simple trend prediction based on recent data
        query = """
        INSERT INTO analytics_summary (metric_name, metric_value, created_at)
        SELECT 
            'trend_prediction' as metric_name,
            json_build_object(
                'total_incidents', COUNT(*),
                'avg_severity', AVG(CASE 
                    WHEN severity = 'high' THEN 3
                    WHEN severity = 'medium' THEN 2
                    ELSE 1
                END),
                'prediction_date', NOW()
            )::text as metric_value,
            NOW() as created_at
        FROM incidents_clean
        WHERE created_at >= NOW() - INTERVAL '7 days';
        """
        
        cur.execute(query)
        conn.commit()
        
        print(f"Trends predicted successfully at {datetime.now()}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error predicting trends: {e}")

def predict_by_governorate():
    """Predict crime trends by governorate"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Predict trends by governorate
        query = """
        INSERT INTO analytics_summary (metric_name, metric_value, created_at)
        SELECT 
            'governorate_prediction_' || governorate_id as metric_name,
            json_build_object(
                'governorate_id', governorate_id,
                'incident_count', COUNT(*),
                'avg_severity', AVG(CASE 
                    WHEN severity = 'high' THEN 3
                    WHEN severity = 'medium' THEN 2
                    ELSE 1
                END),
                'prediction_date', NOW()
            )::text as metric_value,
            NOW() as created_at
        FROM incidents_clean
        WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY governorate_id;
        """
        
        cur.execute(query)
        conn.commit()
        
        print(f"Governorate predictions completed successfully at {datetime.now()}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error predicting by governorate: {e}")
