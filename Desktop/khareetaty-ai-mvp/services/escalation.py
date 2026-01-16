import yaml
import psycopg2
import os
from datetime import datetime, timedelta
import logging

from services.notifications import send_whatsapp, send_sms, send_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_CONN = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME", "khareetaty_ai"),
    "user": os.getenv("DB_USER", "bader"),
    "password": os.getenv("DB_PASSWORD", "secret123")
}

class EscalationEngine:
    def __init__(self, config_path="config/escalation.yaml"):
        """Initialize escalation engine with configuration"""
        self.config = self.load_config(config_path)
        self.conn = None
    
    def load_config(self, config_path):
        """Load escalation configuration from YAML"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load escalation config: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        """Return default escalation configuration"""
        return {
            "thresholds": {
                "low": {"score": 10},
                "medium": {"score": 20},
                "high": {"score": 40},
                "critical": {"score": 60}
            }
        }
    
    def connect_db(self):
        """Connect to database"""
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(**DB_CONN)
    
    def close_db(self):
        """Close database connection"""
        if self.conn and not self.conn.closed:
            self.conn.close()
    
    def determine_severity(self, score):
        """Determine severity level based on score"""
        thresholds = self.config.get("thresholds", {})
        
        if score >= thresholds.get("critical", {}).get("score", 60):
            return "critical"
        elif score >= thresholds.get("high", {}).get("score", 40):
            return "high"
        elif score >= thresholds.get("medium", {}).get("score", 20):
            return "medium"
        elif score >= thresholds.get("low", {}).get("score", 10):
            return "low"
        else:
            return None
    
    def check_cooldown(self, zone, incident_type=None):
        """Check if zone/type is in cooldown period"""
        self.connect_db()
        cur = self.conn.cursor()
        
        cooldown_config = self.config.get("cooldown", {})
        zone_cooldown = cooldown_config.get("same_zone_minutes", 30)
        type_cooldown = cooldown_config.get("same_type_minutes", 15)
        
        # Check zone cooldown
        cur.execute("""
            SELECT COUNT(*) FROM alerts_log
            WHERE message LIKE %s
            AND sent_at >= NOW() - INTERVAL '%s minutes'
        """, (f"%{zone}%", zone_cooldown))
        
        if cur.fetchone()[0] > 0:
            logger.info(f"Zone {zone} is in cooldown period")
            return True
        
        return False
    
    def get_recipients_for_severity(self, severity):
        """Get list of recipients based on severity level"""
        self.connect_db()
        cur = self.conn.cursor()
        
        threshold_config = self.config.get("thresholds", {}).get(severity, {})
        notify_rules = threshold_config.get("notify", [])
        
        recipients = []
        
        for rule in notify_rules:
            if "role" in rule:
                # Get users by role
                cur.execute("""
                    SELECT phone FROM system_users
                    WHERE role = %s AND active = true AND phone IS NOT NULL
                """, (rule["role"],))
                recipients.extend([row[0] for row in cur.fetchall()])
            elif "phone" in rule:
                # Direct phone number
                recipients.append(rule["phone"])
        
        return list(set(recipients))  # Remove duplicates
    
    def format_message(self, severity, zone, score):
        """Format alert message based on template"""
        threshold_config = self.config.get("thresholds", {}).get(severity, {})
        template = threshold_config.get("message_template", 
                                       f"Alert: Hotspot in {zone} with score {score}")
        
        return template.format(zone=zone, score=score)
    
    def send_escalation_alert(self, zone, score, severity):
        """Send escalation alert to appropriate recipients"""
        # Check cooldown
        if self.check_cooldown(zone):
            logger.info(f"Skipping alert for {zone} - in cooldown")
            return False
        
        # Get recipients
        recipients = self.get_recipients_for_severity(severity)
        if not recipients:
            logger.warning(f"No recipients found for severity {severity}")
            return False
        
        # Format message
        message = self.format_message(severity, zone, score)
        
        # Get channels
        threshold_config = self.config.get("thresholds", {}).get(severity, {})
        channels = threshold_config.get("channels", ["whatsapp"])
        
        # Send notifications
        sent_count = 0
        for recipient in recipients:
            for channel in channels:
                try:
                    if channel == "whatsapp":
                        send_whatsapp(recipient, message)
                    elif channel == "sms":
                        send_sms(recipient, message)
                    elif channel == "email":
                        send_email([recipient], f"Alert: {severity.upper()}", message)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send {channel} to {recipient}: {e}")
        
        # Log alert
        self.connect_db()
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO alerts_log (alert_type, severity, message, sent_at, recipients)
            VALUES (%s, %s, %s, NOW(), %s)
        """, ("ESCALATION", severity.upper(), message, ",".join(recipients)))
        self.conn.commit()
        
        logger.info(f"Escalation alert sent: {severity} for {zone} to {len(recipients)} recipients")
        return True
    
    def process_hotspots(self):
        """Process all hotspots and trigger escalations as needed"""
        self.connect_db()
        cur = self.conn.cursor()
        
        # Get all active hotspots
        cur.execute("""
            SELECT zone, score FROM zones_hotspots
            WHERE predicted = false
            ORDER BY score DESC
        """)
        
        hotspots = cur.fetchall()
        escalated_count = 0
        
        for zone, score in hotspots:
            severity = self.determine_severity(float(score))
            
            if severity:
                if self.send_escalation_alert(zone, float(score), severity):
                    escalated_count += 1
        
        self.close_db()
        
        logger.info(f"Processed {len(hotspots)} hotspots, escalated {escalated_count}")
        return {"processed": len(hotspots), "escalated": escalated_count}
    
    def check_incident_patterns(self):
        """Check for incident patterns that require escalation"""
        self.connect_db()
        cur = self.conn.cursor()
        
        incident_rules = self.config.get("incident_types", {})
        escalated = []
        
        for incident_type, rules in incident_rules.items():
            escalate_count = rules.get("escalate_after_count", 999)
            
            # Check if threshold exceeded in last 24 hours
            cur.execute("""
                SELECT zone, COUNT(*) as count
                FROM incidents_clean
                WHERE incident_type = %s
                AND timestamp >= NOW() - INTERVAL '24 hours'
                GROUP BY zone
                HAVING COUNT(*) >= %s
            """, (incident_type, escalate_count))
            
            for zone, count in cur.fetchall():
                message = f"⚠️ Pattern Alert: {count} {incident_type} incidents in {zone} (last 24h)"
                
                # Send to superadmins
                cur.execute("""
                    SELECT phone FROM system_users
                    WHERE role = 'superadmin' AND active = true AND phone IS NOT NULL
                """)
                recipients = [row[0] for row in cur.fetchall()]
                
                for recipient in recipients:
                    try:
                        send_whatsapp(recipient, message)
                    except Exception as e:
                        logger.error(f"Failed to send pattern alert: {e}")
                
                escalated.append({"zone": zone, "type": incident_type, "count": count})
        
        self.close_db()
        return escalated


def run_escalation_check():
    """Run escalation check (called by scheduler or manually)"""
    engine = EscalationEngine()
    
    # Process hotspots
    hotspot_results = engine.process_hotspots()
    
    # Check incident patterns
    pattern_results = engine.check_incident_patterns()
    
    return {
        "hotspots": hotspot_results,
        "patterns": pattern_results
    }


if __name__ == "__main__":
    results = run_escalation_check()
    print(f"Escalation check complete: {results}")
