"""Alert triggering automation"""
import psycopg2
import os
import requests
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "khareetaty_ai"),
        user=os.getenv("DB_USER", "bdr.ai"),
        password=os.getenv("DB_PASSWORD", "secret123"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )

def trigger_alerts():
    """Trigger alerts for high-severity incidents"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get high-severity incidents from last 24 hours
        query = """
        SELECT id, incident_type, severity, location, created_at
        FROM incidents_clean
        WHERE severity = 'high'
        AND created_at >= NOW() - INTERVAL '24 hours'
        AND id NOT IN (
            SELECT incident_id FROM alerts_log WHERE sent_at >= NOW() - INTERVAL '24 hours'
        )
        LIMIT 10;
        """
        
        cur.execute(query)
        incidents = cur.fetchall()
        
        if incidents:
            # Get contacts to notify
            cur.execute("SELECT phone_number, name FROM contacts WHERE active = true")
            contacts = cur.fetchall()
            
            for incident in incidents:
                incident_id, incident_type, severity, location, created_at = incident
                message = f"🚨 High Priority Alert: {incident_type} at {location}. Time: {created_at}"
                
                # Send alerts to contacts
                for phone, name in contacts:
                    send_whatsapp_alert(phone, message)
                    
                    # Log the alert
                    cur.execute(
                        "INSERT INTO alerts_log (incident_id, contact_phone, message, sent_at) VALUES (%s, %s, %s, NOW())",
                        (incident_id, phone, message)
                    )
            
            conn.commit()
            print(f"Sent {len(incidents)} alerts to {len(contacts)} contacts")
        else:
            print("No new high-severity incidents to alert")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error triggering alerts: {e}")

def send_whatsapp_alert(phone: str, message: str):
    """Send WhatsApp alert using API"""
    try:
        # WhatsApp Business API endpoint
        api_token = os.getenv("WHATSAPP_API_TOKEN", "")
        api_url = os.getenv("WHATSAPP_API_URL", "https://api.whatsapp.com/send")
        
        if not api_token:
            print(f"WhatsApp API token not configured, skipping alert to {phone}")
            return
        
        payload = {
            "phone": phone,
            "message": message
        }
        
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"Alert sent successfully to {phone}")
        else:
            print(f"Failed to send alert to {phone}: {response.status_code}")
            
    except Exception as e:
        print(f"Error sending WhatsApp alert to {phone}: {e}")

def trigger_hotspot_alerts():
    """Trigger alerts for hotspot zones"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get high-severity hotspots
        query = """
        SELECT zone_id, incident_count, severity_score
        FROM zones_hotspots
        WHERE severity_score >= 2.5
        ORDER BY severity_score DESC
        LIMIT 5;
        """
        
        cur.execute(query)
        hotspots = cur.fetchall()
        
        if hotspots:
            # Get contacts to notify
            cur.execute("SELECT phone_number, name FROM contacts WHERE active = true")
            contacts = cur.fetchall()
            
            for zone_id, incident_count, severity_score in hotspots:
                message = f"🔥 Hotspot Alert: Zone {zone_id} has {incident_count} incidents with severity {severity_score:.2f}"
                
                for phone, name in contacts:
                    send_whatsapp_alert(phone, message)
            
            print(f"Sent hotspot alerts for {len(hotspots)} zones")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error triggering hotspot alerts: {e}")

def trigger_forecast_alerts():
    """Trigger alerts based on forecast predictions"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get recent predictions with high risk
        query = """
        SELECT metric_name, metric_value
        FROM analytics_summary
        WHERE metric_name LIKE 'trend_prediction%'
        AND created_at >= NOW() - INTERVAL '24 hours'
        ORDER BY created_at DESC
        LIMIT 5;
        """
        
        cur.execute(query)
        predictions = cur.fetchall()
        
        if predictions:
            # Get contacts to notify
            cur.execute("SELECT phone_number, name FROM contacts WHERE active = true")
            contacts = cur.fetchall()
            
            for metric_name, metric_value in predictions:
                message = f"📊 Forecast Alert: {metric_name} - {metric_value}"
                
                for phone, name in contacts:
                    send_whatsapp_alert(phone, message)
            
            print(f"Sent forecast alerts for {len(predictions)} predictions")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error triggering forecast alerts: {e}")
