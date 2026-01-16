"""
Alert system module for Khareetaty AI MVP Crime Analytics System
Handles threshold detection and notification system for alerts
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
import json
import requests
import time

from src.config import Config
from src.database import db_manager

logger = logging.getLogger(__name__)

class AlertSystem:
    def __init__(self):
        self.high_threshold = Config.HIGH_INCIDENT_THRESHOLD
        self.medium_threshold = Config.MEDIUM_INCIDENT_THRESHOLD
        self.alert_cooldown_hours = Config.ALERT_COOLDOWN_HOURS
        self.enable_email_alerts = Config.ENABLE_EMAIL_ALERTS
        self.enable_sms_alerts = Config.ENABLE_SMS_ALERTS
        self.enable_whatsapp_alerts = Config.ENABLE_WHATSAPP_ALERTS
        
    def check_incident_thresholds(self, df, threshold_type: str = 'daily') -> List[Dict]:
        """Check if incident counts exceed configured thresholds"""
        if df.empty:
            return []
            
        alerts = []
        
        # Group by relevant dimensions based on threshold type
        if threshold_type == 'daily':
            # Group by date, zone, and crime type
            grouped = df.groupby([df['timestamp'].dt.date, 'governorate', 'normalized_type']).size().reset_index(name='incident_count')
        elif threshold_type == 'hourly':
            # Group by hour, zone, and crime type
            df['hour'] = df['timestamp'].dt.floor('H')
            grouped = df.groupby(['hour', 'governorate', 'normalized_type']).size().reset_index(name='incident_count')
        else:
            # Default to daily
            grouped = df.groupby([df['timestamp'].dt.date, 'governorate', 'normalized_type']).size().reset_index(name='incident_count')
        
        # Check thresholds
        for _, row in grouped.iterrows():
            incident_count = row['incident_count']
            zone = row.get('governorate', 'Unknown')
            crime_type = row.get('normalized_type', 'ALL')
            
            if threshold_type == 'daily':
                date = str(row[0])  # Date
            elif threshold_type == 'hourly':
                date = str(row['hour'])
            else:
                date = str(row[0])
                
            if incident_count >= self.high_threshold:
                severity = 'HIGH'
                alert_type = 'THRESHOLD_EXCEEDED'
            elif incident_count >= self.medium_threshold:
                severity = 'MEDIUM'
                alert_type = 'THRESHOLD_WARNING'
            else:
                continue  # Below threshold, no alert needed
                
            # Check if similar alert was sent recently (cooldown)
            recent_similar_alerts = self.check_alert_cooldown(alert_type, severity, zone, crime_type)
            
            if not recent_similar_alerts:
                alert = {
                    'alert_type': alert_type,
                    'severity': severity,
                    'zone': zone,
                    'crime_type': crime_type,
                    'incident_count': incident_count,
                    'date': date,
                    'timestamp': datetime.now()
                }
                alerts.append(alert)
            else:
                logger.info(f"Skipping alert for {zone} {crime_type} - cooldown active")
        
        return alerts
        
    def check_alert_cooldown(self, alert_type: str, severity: str, zone: str, crime_type: str) -> bool:
        """Check if a similar alert was sent within the cooldown period"""
        cutoff_time = datetime.now() - timedelta(hours=self.alert_cooldown_hours)
        
        query = """
            SELECT COUNT(*) as count
            FROM alerts_log 
            WHERE alert_type = %s 
              AND severity = %s 
              AND sent_at >= %s
              AND message LIKE %s
        """
        
        # Create a partial match for the message to find similar alerts
        message_pattern = f"%{zone}%{crime_type}%"
        
        try:
            results = db_manager.execute_query(query, (alert_type, severity, cutoff_time, message_pattern))
            return results[0]['count'] > 0
        except Exception as e:
            logger.error(f"Error checking alert cooldown: {e}")
            return False  # If there's an error, assume no cooldown to be safe
            
    def check_hotspot_alerts(self, hotspots: List[Dict]) -> List[Dict]:
        """Check for critical hotspots that require alerts"""
        alerts = []
        
        for hotspot in hotspots:
            severity = hotspot.get('severity', 'LOW')
            zone_name = hotspot.get('zone_name', 'Unknown')
            incident_count = hotspot.get('incident_count', 0)
            latitude = hotspot.get('latitude')
            longitude = hotspot.get('longitude')
            
            if severity in ['CRITICAL', 'HIGH']:
                # Check cooldown for this specific location
                location_key = f"{latitude}_{longitude}"[:50]  # Limit length for DB
                recent_similar_alerts = self.check_hotspot_cooldown(location_key)
                
                if not recent_similar_alerts:
                    alert = {
                        'alert_type': 'HOTSPOT_DETECTED',
                        'severity': severity,
                        'zone_name': zone_name,
                        'incident_count': incident_count,
                        'latitude': latitude,
                        'longitude': longitude,
                        'cluster_id': hotspot.get('cluster_id'),
                        'timestamp': datetime.now()
                    }
                    alerts.append(alert)
                else:
                    logger.info(f"Skipping hotspot alert for {zone_name} - cooldown active")
        
        return alerts
        
    def check_hotspot_cooldown(self, location_key: str) -> bool:
        """Check if a hotspot alert was sent for this location recently"""
        cutoff_time = datetime.now() - timedelta(hours=self.alert_cooldown_hours)
        
        query = """
            SELECT COUNT(*) as count
            FROM alerts_log 
            WHERE alert_type = 'HOTSPOT_DETECTED'
              AND message LIKE %s
              AND sent_at >= %s
        """
        
        try:
            results = db_manager.execute_query(query, (f"%{location_key}%", cutoff_time))
            return results[0]['count'] > 0
        except Exception as e:
            logger.error(f"Error checking hotspot cooldown: {e}")
            return False
            
    def check_trend_alerts(self, trend_data: Dict) -> List[Dict]:
        """Check for concerning trend patterns that require alerts"""
        alerts = []
        
        if not trend_data:
            return alerts
            
        trend_direction = trend_data.get('trend_direction', 'STABLE')
        recent_average = trend_data.get('recent_average', 0)
        overall_average = trend_data.get('overall_average', 0)
        
        if trend_direction == 'INCREASING':
            # Calculate increase percentage
            if overall_average > 0:
                increase_percentage = ((recent_average - overall_average) / overall_average) * 100
                
                if increase_percentage >= 50:  # 50% increase triggers alert
                    severity = 'HIGH' if increase_percentage >= 100 else 'MEDIUM'
                    
                    # Check cooldown
                    recent_similar_alerts = self.check_trend_cooldown('INCREASING')
                    
                    if not recent_similar_alerts:
                        alert = {
                            'alert_type': 'TREND_ANOMALY',
                            'severity': severity,
                            'trend_direction': trend_direction,
                            'increase_percentage': round(increase_percentage, 2),
                            'recent_average': recent_average,
                            'overall_average': overall_average,
                            'timestamp': datetime.now()
                        }
                        alerts.append(alert)
                    else:
                        logger.info("Skipping trend alert - cooldown active")
        
        return alerts
        
    def check_trend_cooldown(self, trend_type: str) -> bool:
        """Check if a trend alert was sent recently"""
        cutoff_time = datetime.now() - timedelta(hours=self.alert_cooldown_hours)
        
        query = """
            SELECT COUNT(*) as count
            FROM alerts_log 
            WHERE alert_type = 'TREND_ANOMALY'
              AND message LIKE %s
              AND sent_at >= %s
        """
        
        try:
            results = db_manager.execute_query(query, (f"%{trend_type}%", cutoff_time))
            return results[0]['count'] > 0
        except Exception as e:
            logger.error(f"Error checking trend cooldown: {e}")
            return False
            
    def generate_alert_message(self, alert: Dict) -> str:
        """Generate human-readable alert message"""
        alert_type = alert['alert_type']
        
        if alert_type == 'THRESHOLD_EXCEEDED':
            return (f"HIGH INCIDENT ALERT: {alert['incident_count']} incidents of type '{alert['crime_type']}' "
                   f"reported in {alert['zone']} on {alert['date']}. Threshold exceeded.")
        elif alert_type == 'THRESHOLD_WARNING':
            return (f"MEDIUM INCIDENT WARNING: {alert['incident_count']} incidents of type '{alert['crime_type']}' "
                   f"reported in {alert['zone']} on {alert['date']}. Approaching threshold.")
        elif alert_type == 'HOTSPOT_DETECTED':
            return (f"HOTSPOT ALERT: Critical hotspot detected in {alert['zone_name']} "
                   f"(Lat: {alert['latitude']}, Lon: {alert['longitude']}). "
                   f"Severity: {alert['severity']}, Incidents: {alert['incident_count']}.")
        elif alert_type == 'TREND_ANOMALY':
            return (f"TREND ANOMALY: Incident trend is {alert['trend_direction']}. "
                   f"Increase of {alert['increase_percentage']}% compared to historical average.")
        else:
            return f"ALERT: {alert_type} - {json.dumps(alert)}"
            
    def send_email_alert(self, subject: str, message: str, recipients: List[str]) -> bool:
        """Send email alert"""
        if not self.enable_email_alerts or not Config.EMAIL_USER or not Config.EMAIL_PASSWORD:
            logger.info("Email alerts disabled or not configured")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = Config.EMAIL_USER
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
            server.starttls()
            server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            
            text = msg.as_string()
            server.sendmail(Config.EMAIL_USER, recipients, text)
            server.quit()
            
            logger.info(f"Email alert sent to {recipients}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
            
    def send_sms_alert(self, message: str, phone_numbers: List[str]) -> bool:
        """Send SMS alert (placeholder - would integrate with actual SMS service)"""
        if not self.enable_sms_alerts:
            logger.info("SMS alerts disabled")
            return False
            
        try:
            # Placeholder for SMS service integration
            # Would typically use services like Twilio, AWS SNS, etc.
            logger.info(f"SMS alert sent to {phone_numbers}: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS alert: {e}")
            return False
            
    def send_whatsapp_alert(self, message: str, phone_numbers: List[str]) -> bool:
        """Send WhatsApp alert (placeholder - would integrate with actual WhatsApp service)"""
        if not self.enable_whatsapp_alerts:
            logger.info("WhatsApp alerts disabled")
            return False
            
        try:
            # Placeholder for WhatsApp service integration
            # Would typically use services like Twilio, WhatsApp Business API, etc.
            logger.info(f"WhatsApp alert sent to {phone_numbers}: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to send WhatsApp alert: {e}")
            return False
            
    def send_alert_notifications(self, alert: Dict) -> List[str]:
        """Send alert notifications through configured channels"""
        message = self.generate_alert_message(alert)
        subject = f"Khareetaty AI Alert: {alert['alert_type']} - {alert['severity']}"
        
        sent_channels = []
        
        # Send email alerts
        if self.enable_email_alerts and Config.ADMIN_EMAILS:
            success = self.send_email_alert(subject, message, Config.ADMIN_EMAILS)
            if success:
                sent_channels.append('email')
        
        # Send SMS alerts
        if self.enable_sms_alerts and Config.ADMIN_PHONES:
            success = self.send_sms_alert(message, Config.ADMIN_PHONES)
            if success:
                sent_channels.append('sms')
        
        # Send WhatsApp alerts
        if self.enable_whatsapp_alerts and Config.ADMIN_PHONES:
            success = self.send_whatsapp_alert(message, Config.ADMIN_PHONES)
            if success:
                sent_channels.append('whatsapp')
        
        return sent_channels
        
    def log_alert(self, alert: Dict, sent_channels: List[str]) -> int:
        """Log alert to database"""
        message = self.generate_alert_message(alert)
        recipients = []
        
        if 'email' in sent_channels and Config.ADMIN_EMAILS:
            recipients.extend(Config.ADMIN_EMAILS)
        if ('sms' in sent_channels or 'whatsapp' in sent_channels) and Config.ADMIN_PHONES:
            recipients.extend(Config.ADMIN_PHONES)
        
        # Get related incident IDs if available
        related_incidents = alert.get('related_incidents', [])
        
        alert_id = db_manager.log_alert(
            alert['alert_type'],
            alert['severity'],
            message,
            recipients,
            related_incidents if related_incidents else None
        )
        
        return alert_id
        
    def process_alerts(self, alerts: List[Dict]) -> Dict:
        """Process a list of alerts and send notifications"""
        if not alerts:
            logger.info("No alerts to process")
            return {'sent': 0, 'failed': 0}
            
        results = {'sent': 0, 'failed': 0}
        
        for alert in alerts:
            try:
                # Send notifications
                sent_channels = self.send_alert_notifications(alert)
                
                if sent_channels:
                    # Log the alert
                    alert_id = self.log_alert(alert, sent_channels)
                    results['sent'] += 1
                    logger.info(f"Alert {alert_id} processed successfully via {sent_channels}")
                else:
                    results['failed'] += 1
                    logger.warning(f"No channels available to send alert: {alert}")
                    
            except Exception as e:
                results['failed'] += 1
                logger.error(f"Failed to process alert: {e}")
        
        logger.info(f"Alert processing completed: {results['sent']} sent, {results['failed']} failed")
        return results
        
    def generate_comprehensive_alerts(self, df=None, hotspots=None, trend_data=None) -> List[Dict]:
        """Generate all types of alerts from available data"""
        all_alerts = []
        
        # Get data if not provided
        if df is None:
            # Query recent incidents from database
            cutoff_date = datetime.now() - timedelta(days=7)  # Last 7 days
            query = """
                SELECT timestamp, normalized_type, governorate, latitude, longitude
                FROM incidents_clean 
                WHERE timestamp >= %s
                ORDER BY timestamp
            """
            incidents_data = db_manager.execute_query(query, (cutoff_date,))
            
            if incidents_data:
                df = pd.DataFrame(incidents_data)
            else:
                df = pd.DataFrame()
        
        # Check incident thresholds
        if not df.empty:
            daily_alerts = self.check_incident_thresholds(df, 'daily')
            hourly_alerts = self.check_incident_thresholds(df, 'hourly')
            all_alerts.extend(daily_alerts)
            all_alerts.extend(hourly_alerts)
        
        # Check hotspots
        if hotspots:
            hotspot_alerts = self.check_hotspot_alerts(hotspots)
            all_alerts.extend(hotspot_alerts)
        
        # Check trends
        if trend_data:
            trend_alerts = self.check_trend_alerts(trend_data)
            all_alerts.extend(trend_alerts)
        
        return all_alerts
        
    def run_alert_detection_cycle(self) -> Dict:
        """Run a complete alert detection cycle"""
        logger.info("Starting alert detection cycle...")
        
        # Get recent data
        cutoff_date = datetime.now() - timedelta(days=7)  # Last 7 days for analysis
        query = """
            SELECT timestamp, normalized_type, governorate, latitude, longitude
            FROM incidents_clean 
            WHERE timestamp >= %s
            ORDER BY timestamp
        """
        
        incidents_data = db_manager.execute_query(query, (cutoff_date,))
        
        if incidents_data:
            df = pd.DataFrame(incidents_data)
        else:
            df = pd.DataFrame()
        
        # Get recent hotspots
        hotspot_cutoff = datetime.now() - timedelta(days=1)  # Last 24 hours
        hotspot_query = """
            SELECT * FROM zones_hotspots
            WHERE created_at >= %s
            ORDER BY risk_score DESC
        """
        
        hotspot_data = db_manager.execute_query(hotspot_query, (hotspot_cutoff,))
        
        # Get recent trend alerts (if any trend data is stored separately)
        # For now, we'll use the incident data to calculate trends
        trend_data = {}  # This would come from analytics module
        
        # Generate all alerts
        alerts = self.generate_comprehensive_alerts(df, hotspot_data, trend_data)
        
        # Process alerts
        results = self.process_alerts(alerts)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'alerts_generated': len(alerts),
            'alerts_sent': results['sent'],
            'alerts_failed': results['failed'],
            'alert_details': alerts
        }
        
        logger.info(f"Alert detection cycle completed: {summary}")
        return summary
        
    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Get recently generated alerts"""
        return db_manager.get_recent_alerts(hours)
        
    def configure_alert_settings(self, high_threshold: int = None, medium_threshold: int = None, 
                                cooldown_hours: int = None, enable_email: bool = None, 
                                enable_sms: bool = None, enable_whatsapp: bool = None):
        """Update alert configuration settings"""
        if high_threshold is not None:
            self.high_threshold = high_threshold
        if medium_threshold is not None:
            self.medium_threshold = medium_threshold
        if cooldown_hours is not None:
            self.alert_cooldown_hours = cooldown_hours
        if enable_email is not None:
            self.enable_email_alerts = enable_email
        if enable_sms is not None:
            self.enable_sms_alerts = enable_sms
        if enable_whatsapp is not None:
            self.enable_whatsapp_alerts = enable_whatsapp
            
        logger.info("Alert settings updated")