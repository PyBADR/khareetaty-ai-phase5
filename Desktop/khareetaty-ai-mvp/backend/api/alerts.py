from fastapi import APIRouter, HTTPException, Depends
import sys
import os
from datetime import datetime
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from automation.trigger_alerts import send_whatsapp_alert, trigger_hotspot_alerts, trigger_forecast_alerts
from utils.auth import require_role

router = APIRouter()

@router.post("/send")
def send_alert(
    message: str,
    phone: Optional[str] = None,
    user: dict = Depends(require_role(["analyst", "superadmin"]))
):
    """
    Send a WhatsApp alert immediately
    
    Args:
        message: Alert message to send
        phone: Optional phone number (uses default if not provided)
        user: Authenticated user (from token)
    
    Returns:
        Status of alert delivery
    """
    try:
        # Get phone from env if not provided
        if not phone:
            phone = os.getenv("WHATSAPP_TO", "whatsapp:+96566338736")
        
        # Ensure phone has whatsapp: prefix
        if not phone.startswith("whatsapp:"):
            phone = f"whatsapp:{phone}"
        
        # Send alert
        result = send_whatsapp_alert(message, phone)
        
        return {
            "status": "success",
            "message": "Alert sent successfully",
            "to": phone,
            "sent_by": user.get("email", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send alert: {str(e)}")

@router.post("/trigger-hotspot")
def trigger_hotspot_alert(user: dict = Depends(require_role(["analyst", "superadmin"]))):
    """
    Trigger hotspot detection alerts based on current data
    
    Requires: analyst or superadmin role
    """
    try:
        result = trigger_hotspot_alerts()
        return {
            "status": "success",
            "message": "Hotspot alerts triggered",
            "executed_by": user.get("email", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger hotspot alerts: {str(e)}")

@router.post("/trigger-forecast")
def trigger_forecast_alert(user: dict = Depends(require_role(["analyst", "superadmin"]))):
    """
    Trigger forecast alerts based on predictions
    
    Requires: analyst or superadmin role
    """
    try:
        result = trigger_forecast_alerts()
        return {
            "status": "success",
            "message": "Forecast alerts triggered",
            "executed_by": user.get("email", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger forecast alerts: {str(e)}")

@router.get("/history")
def get_alert_history(limit: int = 50):
    """
    Get recent alert history from database
    
    Args:
        limit: Maximum number of alerts to return (default 50)
    """
    try:
        import psycopg2
        from backend.db.database import get_db_connection
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Query alerts_log table
        cur.execute("""
            SELECT id, alert_type, zone, governorate, district, police_zone,
                   message, phone, status, created_at
            FROM alerts_log
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        alerts = []
        for row in rows:
            alerts.append({
                "id": row[0],
                "alert_type": row[1],
                "zone": row[2],
                "governorate": row[3],
                "district": row[4],
                "police_zone": row[5],
                "message": row[6],
                "phone": row[7],
                "status": row[8],
                "created_at": row[9].isoformat() if row[9] else None
            })
        
        return {
            "status": "success",
            "count": len(alerts),
            "data": alerts
        }
    except Exception as e:
        # If table doesn't exist yet, return empty
        return {
            "status": "success",
            "count": 0,
            "data": [],
            "note": "alerts_log table not yet created or error occurred"
        }

@router.get("/stats")
def get_alert_stats():
    """
    Get alert statistics
    """
    try:
        import psycopg2
        from backend.db.database import get_db_connection
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get stats
        cur.execute("""
            SELECT 
                COUNT(*) as total_alerts,
                COUNT(CASE WHEN DATE(created_at) = CURRENT_DATE THEN 1 END) as today_alerts,
                COUNT(CASE WHEN status = 'sent' THEN 1 END) as successful_alerts,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_alerts
            FROM alerts_log
        """)
        
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        return {
            "status": "success",
            "data": {
                "total_alerts": row[0] if row else 0,
                "today_alerts": row[1] if row else 0,
                "successful_alerts": row[2] if row else 0,
                "failed_alerts": row[3] if row else 0
            }
        }
    except Exception as e:
        return {
            "status": "success",
            "data": {
                "total_alerts": 0,
                "today_alerts": 0,
                "successful_alerts": 0,
                "failed_alerts": 0
            },
            "note": "alerts_log table not yet created or error occurred"
        }
