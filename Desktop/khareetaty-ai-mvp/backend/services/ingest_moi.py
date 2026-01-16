"""
MOI (Ministry of Interior) Data Ingestion Service
Handles incident reports, patrol logs, and 112 call metadata
"""

import psycopg2
import logging
from datetime import datetime
from typing import Dict, Any
from services.data_broker import get_broker, DataSource

logger = logging.getLogger(__name__)

DB_CONN = {
    "host": "postgres",
    "dbname": "khareetaty_ai",
    "user": "bader",
    "password": "secret123"
}

class MOIIngestionService:
    """
    Ingests data from MOI systems:
    - Incident reports
    - 112 emergency call metadata
    - Patrol activity logs
    """
    
    def __init__(self):
        self.broker = get_broker()
    
    def ingest_incident(self, incident_data: Dict[str, Any]) -> bool:
        """
        Ingest incident from MOI system
        
        Expected format:
        {
            "incident_type": "theft",
            "governorate": "Hawally",
            "zone": "Salmiya",
            "lat": 29.3344,
            "lon": 48.0537,
            "timestamp": "2026-01-16T10:30:00",
            "severity": "medium",
            "description": "Car theft reported"
        }
        """
        try:
            # Validate required fields
            required = ["incident_type", "lat", "lon", "timestamp"]
            if not all(k in incident_data for k in required):
                logger.error("Missing required fields in incident data")
                return False
            
            # Publish to broker
            self.broker.publish_event(DataSource.MOI_INCIDENTS, incident_data)
            
            # Write to database
            conn = psycopg2.connect(**DB_CONN)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO incidents_raw 
                (incident_type, governorate, zone, lat, lon, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                incident_data["incident_type"],
                incident_data.get("governorate", "unknown"),
                incident_data.get("zone", "unknown"),
                incident_data["lat"],
                incident_data["lon"],
                datetime.fromisoformat(incident_data["timestamp"])
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Ingested MOI incident: {incident_data['incident_type']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ingest MOI incident: {e}")
            return False
    
    def ingest_patrol_log(self, patrol_data: Dict[str, Any]) -> bool:
        """
        Ingest patrol activity log
        
        Format:
        {
            "patrol_id": "P-123",
            "zone": "Salmiya",
            "activity": "routine_patrol",
            "lat": 29.3344,
            "lon": 48.0537,
            "timestamp": "2026-01-16T10:30:00"
        }
        """
        try:
            self.broker.publish_event(DataSource.MOI_INCIDENTS, {
                "type": "patrol_log",
                **patrol_data
            })
            logger.info(f"Ingested patrol log: {patrol_data.get('patrol_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest patrol log: {e}")
            return False
    
    def ingest_emergency_call(self, call_data: Dict[str, Any]) -> bool:
        """
        Ingest 112 emergency call metadata (not recording)
        
        Format:
        {
            "call_id": "112-456789",
            "call_type": "medical",
            "location": "Salmiya",
            "lat": 29.3344,
            "lon": 48.0537,
            "timestamp": "2026-01-16T10:30:00",
            "response_time": 180
        }
        """
        try:
            self.broker.publish_event(DataSource.MOI_INCIDENTS, {
                "type": "emergency_call",
                **call_data
            })
            logger.info(f"Ingested emergency call: {call_data.get('call_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest emergency call: {e}")
            return False
