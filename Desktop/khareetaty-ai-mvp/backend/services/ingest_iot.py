"""
IoT & CCTV Metadata Ingestion Service
Handles sensor data and camera metadata (NOT video processing)
"""

import logging
from datetime import datetime
from typing import Dict, Any
from services.data_broker import get_broker, DataSource

logger = logging.getLogger(__name__)

class IoTIngestionService:
    """
    Ingests IoT sensor and CCTV metadata:
    - Motion detection events
    - Crowd density estimates
    - License plate reader (LPR) hits
    - Camera status (online/offline)
    - Environmental sensors
    
    NOTE: This does NOT process video streams, only metadata
    """
    
    def __init__(self):
        self.broker = get_broker()
    
    def ingest_motion_event(self, motion_data: Dict[str, Any]) -> bool:
        """
        Ingest motion detection event from camera
        
        Format:
        {
            "camera_id": "CAM-001",
            "location": "Salmiya Beach",
            "lat": 29.3344,
            "lon": 48.0537,
            "timestamp": "2026-01-16T10:30:00",
            "motion_intensity": "high",
            "duration_seconds": 30
        }
        """
        try:
            self.broker.publish_event(DataSource.IOT_SENSORS, {
                "type": "motion_event",
                **motion_data
            })
            logger.info(f"Ingested motion event: {motion_data.get('camera_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest motion event: {e}")
            return False
    
    def ingest_crowd_density(self, crowd_data: Dict[str, Any]) -> bool:
        """
        Ingest crowd density estimate
        
        Format:
        {
            "camera_id": "CAM-002",
            "location": "Avenues Mall",
            "lat": 29.3344,
            "lon": 48.0537,
            "timestamp": "2026-01-16T10:30:00",
            "density_level": "high",
            "estimated_count": 150
        }
        """
        try:
            self.broker.publish_event(DataSource.CCTV_METADATA, {
                "type": "crowd_density",
                **crowd_data
            })
            logger.info(f"Ingested crowd density: {crowd_data.get('camera_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest crowd density: {e}")
            return False
    
    def ingest_lpr_hit(self, lpr_data: Dict[str, Any]) -> bool:
        """
        Ingest license plate reader hit (count only, not plate numbers)
        
        Format:
        {
            "lpr_id": "LPR-005",
            "location": "Highway 40",
            "lat": 29.3344,
            "lon": 48.0537,
            "timestamp": "2026-01-16T10:30:00",
            "vehicle_count": 45,
            "alert_triggered": false
        }
        """
        try:
            self.broker.publish_event(DataSource.IOT_SENSORS, {
                "type": "lpr_hit",
                **lpr_data
            })
            logger.info(f"Ingested LPR hit: {lpr_data.get('lpr_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest LPR hit: {e}")
            return False
    
    def ingest_camera_status(self, status_data: Dict[str, Any]) -> bool:
        """
        Ingest camera status change
        
        Format:
        {
            "camera_id": "CAM-010",
            "location": "Salmiya",
            "lat": 29.3344,
            "lon": 48.0537,
            "timestamp": "2026-01-16T10:30:00",
            "status": "offline",
            "reason": "connection_lost"
        }
        """
        try:
            self.broker.publish_event(DataSource.CCTV_METADATA, {
                "type": "camera_status",
                **status_data
            })
            
            # Camera offline in high-risk zone = potential risk spike
            if status_data.get("status") == "offline":
                logger.warning(f"Camera offline: {status_data.get('camera_id')} at {status_data.get('location')}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to ingest camera status: {e}")
            return False
    
    def ingest_environmental_sensor(self, sensor_data: Dict[str, Any]) -> bool:
        """
        Ingest environmental sensor data
        
        Format:
        {
            "sensor_id": "ENV-001",
            "sensor_type": "smoke",
            "location": "Industrial Area",
            "lat": 29.3344,
            "lon": 48.0537,
            "timestamp": "2026-01-16T10:30:00",
            "reading": 85,
            "threshold_exceeded": true
        }
        """
        try:
            self.broker.publish_event(DataSource.IOT_SENSORS, {
                "type": "environmental_sensor",
                **sensor_data
            })
            logger.info(f"Ingested environmental sensor: {sensor_data.get('sensor_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest environmental sensor: {e}")
            return False
