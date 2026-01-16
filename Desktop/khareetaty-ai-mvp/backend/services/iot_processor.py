"""
IoT & CCTV Metadata Processor
Processes IoT sensor data and CCTV metadata to detect patterns and anomalies
"""

import psycopg2
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from services.data_broker import get_broker, DataSource

logger = logging.getLogger(__name__)

DB_CONN = {
    "host": "postgres",
    "dbname": "khareetaty_ai",
    "user": "bader",
    "password": "secret123"
}

class IoTProcessor:
    """
    Processes IoT and CCTV metadata to:
    - Detect anomalies (camera offline in high-risk zones)
    - Correlate crowd density with incidents
    - Track environmental hazards
    - Generate risk scores based on sensor data
    """
    
    def __init__(self):
        self.broker = get_broker()
    
    def process_camera_offline_risk(self, zone: str) -> float:
        """
        Calculate risk increase when cameras go offline in a zone
        
        Args:
            zone: Zone name
            
        Returns:
            Risk multiplier (1.0 = no change, >1.0 = increased risk)
        """
        try:
            # Get recent incidents in zone
            conn = psycopg2.connect(**DB_CONN)
            cur = conn.cursor()
            
            # Check incident history in zone
            cur.execute("""
                SELECT COUNT(*) FROM incidents_clean
                WHERE zone = %s
                AND timestamp > NOW() - INTERVAL '7 days'
            """, (zone,))
            
            incident_count = cur.fetchone()[0]
            conn.close()
            
            # High incident zones with offline cameras = higher risk
            if incident_count > 20:
                return 1.5  # 50% risk increase
            elif incident_count > 10:
                return 1.3  # 30% risk increase
            else:
                return 1.1  # 10% risk increase
                
        except Exception as e:
            logger.error(f"Failed to process camera offline risk: {e}")
            return 1.0
    
    def process_crowd_density_correlation(self, location: str, density_level: str) -> Dict:
        """
        Correlate crowd density with incident probability
        
        Args:
            location: Location name
            density_level: Density level (low/medium/high)
            
        Returns:
            Correlation analysis
        """
        try:
            conn = psycopg2.connect(**DB_CONN)
            cur = conn.cursor()
            
            # Get incidents in similar locations during high density
            cur.execute("""
                SELECT incident_type, COUNT(*) as count
                FROM incidents_clean
                WHERE zone LIKE %s
                AND timestamp > NOW() - INTERVAL '30 days'
                GROUP BY incident_type
                ORDER BY count DESC
                LIMIT 5
            """, (f"%{location}%",))
            
            incident_types = cur.fetchall()
            conn.close()
            
            # Calculate risk based on density
            risk_multiplier = {
                "low": 0.8,
                "medium": 1.0,
                "high": 1.4
            }.get(density_level, 1.0)
            
            return {
                "location": location,
                "density_level": density_level,
                "risk_multiplier": risk_multiplier,
                "common_incidents": [{
                    "type": row[0],
                    "count": row[1]
                } for row in incident_types]
            }
            
        except Exception as e:
            logger.error(f"Failed to process crowd density correlation: {e}")
            return {}
    
    def process_motion_anomaly(self, camera_id: str, motion_intensity: str, hour: int) -> bool:
        """
        Detect anomalous motion patterns
        
        Args:
            camera_id: Camera identifier
            motion_intensity: Motion intensity level
            hour: Hour of day (0-23)
            
        Returns:
            True if anomaly detected
        """
        # Unusual motion patterns:
        # - High intensity during late night (2-5 AM)
        # - Sudden change from normal patterns
        
        if motion_intensity == "high" and 2 <= hour <= 5:
            logger.warning(f"Anomalous motion detected: {camera_id} at {hour}:00")
            return True
        
        return False
    
    def process_environmental_alert(self, sensor_type: str, reading: float, threshold: float) -> Dict:
        """
        Process environmental sensor alerts
        
        Args:
            sensor_type: Type of sensor (smoke, temperature, etc.)
            reading: Current reading
            threshold: Alert threshold
            
        Returns:
            Alert information
        """
        if reading > threshold:
            severity = "critical" if reading > threshold * 1.5 else "high"
            
            return {
                "alert": True,
                "severity": severity,
                "sensor_type": sensor_type,
                "reading": reading,
                "threshold": threshold,
                "message": f"{sensor_type} sensor reading {reading} exceeds threshold {threshold}"
            }
        
        return {"alert": False}
    
    def aggregate_iot_risk_score(self, zone: str) -> float:
        """
        Aggregate risk score from all IoT sources in a zone
        
        Args:
            zone: Zone name
            
        Returns:
            Aggregated risk score (0-100)
        """
        try:
            # Consume recent IoT events for zone
            events = self.broker.consume_events(DataSource.IOT_SENSORS, count=100)
            
            risk_factors = []
            
            for event in events:
                data = event.get("data", {})
                event_zone = data.get("location", "")
                
                if zone.lower() in event_zone.lower():
                    event_type = data.get("type")
                    
                    if event_type == "motion_event":
                        intensity = data.get("motion_intensity", "low")
                        if intensity == "high":
                            risk_factors.append(5)
                    
                    elif event_type == "environmental_sensor":
                        if data.get("threshold_exceeded"):
                            risk_factors.append(15)
            
            # Calculate average risk
            if risk_factors:
                return min(sum(risk_factors) / len(risk_factors) * 2, 100)
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to aggregate IoT risk score: {e}")
            return 0
    
    def generate_iot_insights(self) -> List[Dict]:
        """
        Generate insights from IoT data
        
        Returns:
            List of insights
        """
        insights = []
        
        try:
            # Check camera status
            cctv_events = self.broker.consume_events(DataSource.CCTV_METADATA, count=50)
            
            offline_cameras = []
            for event in cctv_events:
                data = event.get("data", {})
                if data.get("type") == "camera_status" and data.get("status") == "offline":
                    offline_cameras.append(data.get("camera_id"))
            
            if offline_cameras:
                insights.append({
                    "type": "camera_offline",
                    "severity": "medium",
                    "message": f"{len(offline_cameras)} cameras offline",
                    "cameras": offline_cameras[:5]  # Top 5
                })
            
            # Check for high crowd density
            high_density_locations = []
            for event in cctv_events:
                data = event.get("data", {})
                if data.get("type") == "crowd_density" and data.get("density_level") == "high":
                    high_density_locations.append(data.get("location"))
            
            if high_density_locations:
                insights.append({
                    "type": "high_crowd_density",
                    "severity": "low",
                    "message": f"High crowd density in {len(high_density_locations)} locations",
                    "locations": list(set(high_density_locations))[:5]
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate IoT insights: {e}")
            return []


if __name__ == "__main__":
    processor = IoTProcessor()
    insights = processor.generate_iot_insights()
    print("IoT Insights:", insights)
