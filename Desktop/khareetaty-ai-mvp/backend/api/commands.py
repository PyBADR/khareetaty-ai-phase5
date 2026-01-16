from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import psycopg2
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.utils.auth import decode_token, require_role
from services.notifications import send_whatsapp, send_sms, send_email

router = APIRouter()

DB_CONN = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME", "khareetaty_ai"),
    "user": os.getenv("DB_USER", "bader"),
    "password": os.getenv("DB_PASSWORD", "secret123")
}

class TaskAssignment(BaseModel):
    zone: str
    severity: str
    assigned_to: str
    description: Optional[str] = ""

class AlertOverride(BaseModel):
    zone: str
    action: str  # 'mute', 'escalate', 'resolve'
    reason: Optional[str] = ""

class ManualAlert(BaseModel):
    message: str
    severity: str
    recipients: List[str]
    channels: List[str]  # ['whatsapp', 'sms', 'email']

# ============================================
# DASHBOARD OVERVIEW
# ============================================

@router.get("/dashboard/overview")
def get_dashboard_overview(user: dict = Depends(decode_token)):
    """
    Get operational overview for command dashboard
    """
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    
    # Active hotspots today
    cur.execute("""
        SELECT COUNT(*) FROM zones_hotspots 
        WHERE predicted = false 
        AND created_at >= CURRENT_DATE
    """)
    active_hotspots = cur.fetchone()[0]
    
    # Incidents in last 24 hours
    cur.execute("""
        SELECT COUNT(*) FROM incidents_clean 
        WHERE timestamp >= NOW() - INTERVAL '24 hours'
    """)
    incidents_24h = cur.fetchone()[0]
    
    # Alerts fired in last 24 hours
    cur.execute("""
        SELECT COUNT(*) FROM alerts_log 
        WHERE sent_at >= NOW() - INTERVAL '24 hours'
    """)
    alerts_24h = cur.fetchone()[0]
    
    # Top 5 hotspots
    cur.execute("""
        SELECT zone, score FROM zones_hotspots 
        WHERE predicted = false 
        ORDER BY score DESC LIMIT 5
    """)
    top_hotspots = [{"zone": row[0], "score": float(row[1])} for row in cur.fetchall()]
    
    # Incidents by governorate (last 7 days)
    cur.execute("""
        SELECT governorate, COUNT(*) as count 
        FROM incidents_clean 
        WHERE timestamp >= NOW() - INTERVAL '7 days'
        GROUP BY governorate 
        ORDER BY count DESC
    """)
    by_governorate = [{"governorate": row[0], "count": row[1]} for row in cur.fetchall()]
    
    # Incidents by type (last 7 days)
    cur.execute("""
        SELECT incident_type, COUNT(*) as count 
        FROM incidents_clean 
        WHERE timestamp >= NOW() - INTERVAL '7 days'
        GROUP BY incident_type 
        ORDER BY count DESC LIMIT 10
    """)
    by_type = [{"type": row[0], "count": row[1]} for row in cur.fetchall()]
    
    conn.close()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "active_hotspots": active_hotspots,
            "incidents_24h": incidents_24h,
            "alerts_24h": alerts_24h
        },
        "top_hotspots": top_hotspots,
        "by_governorate": by_governorate,
        "by_type": by_type
    }

@router.get("/dashboard/tactical")
def get_tactical_view(user: dict = Depends(decode_token)):
    """
    Get tactical view with hourly breakdown and trends
    """
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    
    # Incidents by hour (last 24 hours)
    cur.execute("""
        SELECT hour, COUNT(*) as count 
        FROM incidents_clean 
        WHERE timestamp >= NOW() - INTERVAL '24 hours'
        GROUP BY hour 
        ORDER BY hour
    """)
    by_hour = [{"hour": row[0], "count": row[1]} for row in cur.fetchall()]
    
    # Trending zones (increasing incidents)
    cur.execute("""
        WITH recent AS (
            SELECT zone, COUNT(*) as recent_count
            FROM incidents_clean
            WHERE timestamp >= NOW() - INTERVAL '7 days'
            GROUP BY zone
        ),
        previous AS (
            SELECT zone, COUNT(*) as prev_count
            FROM incidents_clean
            WHERE timestamp >= NOW() - INTERVAL '14 days'
            AND timestamp < NOW() - INTERVAL '7 days'
            GROUP BY zone
        )
        SELECT r.zone, r.recent_count, COALESCE(p.prev_count, 0) as prev_count,
               r.recent_count - COALESCE(p.prev_count, 0) as change
        FROM recent r
        LEFT JOIN previous p ON r.zone = p.zone
        WHERE r.recent_count > COALESCE(p.prev_count, 0)
        ORDER BY change DESC
        LIMIT 10
    """)
    trending_zones = [{
        "zone": row[0], 
        "recent_count": row[1], 
        "prev_count": row[2],
        "change": row[3]
    } for row in cur.fetchall()]
    
    conn.close()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "by_hour": by_hour,
        "trending_zones": trending_zones
    }

# ============================================
# TASK MANAGEMENT
# ============================================

@router.post("/tasks/assign")
def assign_task(
    task: TaskAssignment,
    user: dict = Depends(require_role(["analyst", "superadmin"]))
):
    """
    Assign a task to a team or individual
    """
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    
    # Create assigned_tasks table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS assigned_tasks (
            id SERIAL PRIMARY KEY,
            zone TEXT NOT NULL,
            severity TEXT CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
            assigned_to TEXT NOT NULL,
            assigned_by TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'on-route', 'in-progress', 'resolved', 'cancelled')),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("""
        INSERT INTO assigned_tasks (zone, severity, assigned_to, assigned_by, description)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (task.zone, task.severity, task.assigned_to, user["email"], task.description))
    
    task_id = cur.fetchone()[0]
    
    # Log the action
    cur.execute("""
        INSERT INTO action_log (user_email, action, payload, timestamp)
        VALUES (%s, %s, %s, NOW())
    """, (user["email"], "TASK_ASSIGNED", f"Task {task_id} assigned to {task.assigned_to} for zone {task.zone}"))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "task_id": task_id,
        "message": f"Task assigned to {task.assigned_to}"
    }

@router.get("/tasks/active")
def get_active_tasks(user: dict = Depends(decode_token)):
    """
    Get all active tasks
    """
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, zone, severity, assigned_to, assigned_by, description, status, created_at
        FROM assigned_tasks
        WHERE status IN ('pending', 'on-route', 'in-progress')
        ORDER BY created_at DESC
    """)
    
    tasks = []
    for row in cur.fetchall():
        tasks.append({
            "id": row[0],
            "zone": row[1],
            "severity": row[2],
            "assigned_to": row[3],
            "assigned_by": row[4],
            "description": row[5],
            "status": row[6],
            "created_at": row[7].isoformat() if row[7] else None
        })
    
    conn.close()
    
    return {
        "total": len(tasks),
        "tasks": tasks
    }

@router.post("/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    user: dict = Depends(require_role(["analyst", "superadmin"]))
):
    """
    Mark a task as completed
    """
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE assigned_tasks
        SET status = 'resolved', updated_at = NOW()
        WHERE id = %s
        RETURNING zone
    """, (task_id,))
    
    result = cur.fetchone()
    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    
    zone = result[0]
    
    # Log the action
    cur.execute("""
        INSERT INTO action_log (user_email, action, payload, timestamp)
        VALUES (%s, %s, %s, NOW())
    """, (user["email"], "TASK_COMPLETED", f"Task {task_id} for zone {zone} marked as resolved"))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "message": f"Task {task_id} marked as resolved"
    }

# ============================================
# ALERT MANAGEMENT
# ============================================

@router.post("/alerts/manual")
def send_manual_alert(
    alert: ManualAlert,
    user: dict = Depends(require_role(["analyst", "superadmin"]))
):
    """
    Send manual alert to specified recipients
    """
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    
    sent_count = 0
    failed_count = 0
    
    for recipient in alert.recipients:
        for channel in alert.channels:
            try:
                if channel == 'whatsapp':
                    send_whatsapp(recipient, alert.message)
                elif channel == 'sms':
                    send_sms(recipient, alert.message)
                elif channel == 'email':
                    send_email([recipient], f"Alert: {alert.severity}", alert.message)
                sent_count += 1
            except Exception as e:
                failed_count += 1
                print(f"Failed to send {channel} to {recipient}: {e}")
    
    # Log the alert
    cur.execute("""
        INSERT INTO alerts_log (alert_type, severity, message, sent_at, recipients, status)
        VALUES (%s, %s, %s, NOW(), %s, %s)
    """, ("MANUAL", alert.severity, alert.message, ",".join(alert.recipients), "sent" if sent_count > 0 else "failed"))
    
    # Log the action
    cur.execute("""
        INSERT INTO action_log (user_email, action, payload, timestamp)
        VALUES (%s, %s, %s, NOW())
    """, (user["email"], "MANUAL_ALERT_SENT", f"Alert sent to {len(alert.recipients)} recipients via {alert.channels}"))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "sent": sent_count,
        "failed": failed_count,
        "message": f"Alert sent to {sent_count} recipients"
    }

@router.post("/alerts/override")
def override_alert(
    override: AlertOverride,
    user: dict = Depends(require_role(["analyst", "superadmin"]))
):
    """
    Override alert behavior for a zone (mute, escalate, or resolve)
    """
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    
    # Create alert_overrides table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alert_overrides (
            id SERIAL PRIMARY KEY,
            zone TEXT NOT NULL,
            action TEXT NOT NULL,
            reason TEXT,
            created_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            expires_at TIMESTAMP
        )
    """)
    
    # Set expiration (24 hours for mute, immediate for resolve)
    expires_at = "NOW() + INTERVAL '24 hours'" if override.action == 'mute' else "NOW()"
    
    cur.execute(f"""
        INSERT INTO alert_overrides (zone, action, reason, created_by, expires_at)
        VALUES (%s, %s, %s, %s, {expires_at})
    """, (override.zone, override.action, override.reason, user["email"]))
    
    # Log the action
    cur.execute("""
        INSERT INTO action_log (user_email, action, payload, timestamp)
        VALUES (%s, %s, %s, NOW())
    """, (user["email"], "ALERT_OVERRIDE", f"Zone {override.zone} - {override.action}: {override.reason}"))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "message": f"Alert override applied: {override.action} for zone {override.zone}"
    }

# ============================================
# AUDIT LOG
# ============================================

@router.get("/audit/log")
def get_audit_log(
    limit: int = Query(100, le=1000),
    user: dict = Depends(require_role(["superadmin"]))
):
    """
    Get audit log of all actions (superadmin only)
    """
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    
    # Create action_log table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS action_log (
            id SERIAL PRIMARY KEY,
            user_email TEXT NOT NULL,
            action TEXT NOT NULL,
            payload TEXT,
            timestamp TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("""
        SELECT id, user_email, action, payload, timestamp
        FROM action_log
        ORDER BY timestamp DESC
        LIMIT %s
    """, (limit,))
    
    logs = []
    for row in cur.fetchall():
        logs.append({
            "id": row[0],
            "user": row[1],
            "action": row[2],
            "payload": row[3],
            "timestamp": row[4].isoformat() if row[4] else None
        })
    
    conn.close()
    
    return {
        "total": len(logs),
        "logs": logs
    }
