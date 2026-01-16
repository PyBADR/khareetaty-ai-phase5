import psycopg2
import os
import sys
import logging

# Add parent directory to path to import services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services.notifications import send_whatsapp

logger = logging.getLogger(__name__)

THRESHOLD = int(os.getenv("ALERT_THRESHOLD", 10))  # adjustable threshold

DB_CONN = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME", "khareetaty_ai"),
    "user": os.getenv("DB_USER", "bdr.ai"),
    "password": os.getenv("DB_PASSWORD", "secret123")
}

def trigger_hotspot_alerts():
    """
    Trigger production-ready hotspot activation alerts with zone context
    Sends to multiple WhatsApp contacts
    """
    try:
        conn = psycopg2.connect(**DB_CONN)
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        raise
    
    cur = conn.cursor()
    
    # Query for high-scoring district hotspots with geographic context
    cur.execute("""
        SELECT 
            zh.zone,
            zh.district,
            zh.police_zone,
            zh.score,
            zh.forecast_count,
            zh.created_at
        FROM zones_hotspots zh
        WHERE zh.predicted = false 
        AND zh.zone_type = 'district_cluster'
        AND zh.score > %s
        AND zh.created_at >= NOW() - INTERVAL '1 hour'
        ORDER BY zh.score DESC 
        LIMIT 10;
    """, (THRESHOLD,))
    
    rows = cur.fetchall()

    if not rows:
        logger.info("No hotspots exceeding threshold found")
        conn.close()
        return 0

    # Get multiple WhatsApp contacts from environment
    contacts_str = os.getenv("WHATSAPP_CONTACTS", os.getenv("ADMIN_PHONE", "+96566338736"))
    contacts = [c.strip() for c in contacts_str.split(',')]
    
    triggered_count = 0
    
    for row in rows:
        zone, district, police_zone, score, forecast_count, created_at = row
        
        # Calculate trend (simplified - would need historical data for real trend)
        # For now, use score as proxy
        trend_pct = min(100, score * 2)  # Simplified trend calculation
        
        # Get block info from zone name if available
        block = "N/A"
        if "_cluster_" in zone:
            parts = zone.split("_cluster_")
            if len(parts) > 1:
                block = f"Cluster {parts[1]}"
        
        # Production alert format
        msg = f"""🚨 Hotspot Activation Alert

Zone: {district or 'Unknown'} {block}
Trend: +{trend_pct:.1f}% WoW
Forecast: {forecast_count or 'N/A'} incidents next 24h
Sector: {police_zone or 'Unknown'}
Timestamp: {created_at.strftime('%Y-%m-%d %H:%M') if created_at else 'N/A'}

Source: Khareetaty-AI
"""
        
        # Send to all contacts
        for contact in contacts:
            try:
                send_whatsapp(contact, msg)
                logger.info(f"Alert sent to {contact}: {district}")
            except Exception as e:
                logger.error(f"Failed to send alert to {contact} for {zone}: {e}")
        
        # Log the alert in the database
        cur.execute("""
            INSERT INTO alerts_log (alert_type, severity, message, sent_at, recipients, status)
            VALUES (%s, %s, %s, NOW(), %s, %s)
        """, (
            "HOTSPOT_ACTIVATION", 
            "CRITICAL" if score > THRESHOLD * 2 else "HIGH", 
            msg, 
            ','.join(contacts),
            'sent'
        ))
        
        triggered_count += 1

    conn.commit()
    conn.close()
    logger.info(f"Triggered {triggered_count} hotspot alerts to {len(contacts)} contacts")
    return triggered_count

def send_whatsapp_alert(message: str, phone: str = None):
    """
    Send a WhatsApp alert to specified phone number
    
    Args:
        message: Alert message to send
        phone: Phone number (with or without whatsapp: prefix)
    
    Returns:
        Message SID if successful
    """
    if not phone:
        phone = os.getenv("WHATSAPP_TO", "+96566338736")
    
    # Remove whatsapp: prefix if present for send_whatsapp function
    if phone.startswith("whatsapp:"):
        phone = phone.replace("whatsapp:", "")
    
    return send_whatsapp(phone, message)

def trigger_forecast_alerts():
    """
    Trigger alerts for high-risk forecast predictions
    """
    try:
        conn = psycopg2.connect(**DB_CONN)
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        raise
    
    cur = conn.cursor()
    
    # Query for high forecast predictions
    cur.execute("""
        SELECT 
            district,
            police_zone,
            forecast_count,
            score as trend_pct,
            forecast_timestamp
        FROM zones_hotspots
        WHERE predicted = true
        AND zone_type = 'district_forecast'
        AND forecast_count > %s
        AND forecast_timestamp >= NOW()
        ORDER BY forecast_count DESC
        LIMIT 5;
    """, (THRESHOLD,))
    
    rows = cur.fetchall()
    
    if not rows:
        logger.info("No high-risk forecasts found")
        conn.close()
        return 0
    
    contacts_str = os.getenv("WHATSAPP_CONTACTS", os.getenv("ADMIN_PHONE", "+96566338736"))
    contacts = [c.strip() for c in contacts_str.split(',')]
    
    triggered_count = 0
    
    for row in rows:
        district, police_zone, forecast_count, trend_pct, forecast_time = row
        
        msg = f"""⚠️ High-Risk Forecast Alert

District: {district}
Predicted Incidents: {forecast_count} in next 24h
Trend: {trend_pct:+.1f}%
Police Sector: {police_zone or 'Unknown'}
Forecast Valid Until: {forecast_time.strftime('%Y-%m-%d %H:%M') if forecast_time else 'N/A'}

Recommendation: Increase patrol presence

Source: Khareetaty-AI Predictive Model
"""
        
        for contact in contacts:
            try:
                send_whatsapp(contact, msg)
                logger.info(f"Forecast alert sent to {contact}: {district}")
            except Exception as e:
                logger.error(f"Failed to send forecast alert to {contact}: {e}")
        
        cur.execute("""
            INSERT INTO alerts_log (alert_type, severity, message, sent_at, recipients, status)
            VALUES (%s, %s, %s, NOW(), %s, %s)
        """, ("FORECAST_HIGH_RISK", "MEDIUM", msg, ','.join(contacts), 'sent'))
        
        triggered_count += 1
    
    conn.commit()
    conn.close()
    logger.info(f"Triggered {triggered_count} forecast alerts")
    return triggered_count

def trigger_alerts():
    """Main function to trigger all alert types"""
    hotspot_count = trigger_hotspot_alerts()
    forecast_count = trigger_forecast_alerts()
    return hotspot_count + forecast_count

    conn.commit()
    conn.close()
    logger.info(f"Alert processing complete. {triggered_count} alerts sent.")


if __name__ == "__main__":
    trigger_alerts()