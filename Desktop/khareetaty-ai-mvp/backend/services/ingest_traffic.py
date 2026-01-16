"""
Traffic Data Ingestion Service
Handles traffic incidents, accidents, and road closures
"""

import logging
from datetime import datetime
from typing import Dict, Any
from services.data_broker import get_broker, DataSource

logger = logging.getLogger(__name__)

class TrafficIngestionService:
    """
    Ingests data from Traffic systems:
    - Traffic accidents
    - Road closures
    - Traffic congestion data
    - Speed violations
    """
    
    def __init__(self):
        self.broker = get_broker()
    
    def ingest_accident(self, accident_data: Dict[str, Any]) -> bool:
        """
        Ingest traffic accident
        
        Format:
        {
            "accident_id": "ACC-2026-001",
            "severity": "major",
            "vehicles_involved": 2,
            "injuries": 1,
            "location": "Gulf Road",
            "lat": 29.3344,
            "lon": 48.0537,
            "timestamp": "2026-01-16T10:30:00",
            "road_blocked": true
        }
        """
        try:
            self.broker.publish_event(DataSource.TRAFFIC, {
                "type": "accident",
                **accident_data
            })
            logger.info(f"Ingested traffic accident: {accident_data.get('accident_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest traffic accident: {e}")
            return False
    
    def ingest_road_closure(self, closure_data: Dict[str, Any]) -> bool:
        """
        Ingest road closure
        
        Format:
        {
            "closure_id": "CLOSE-2026-001",
            "road_name": "Gulf Road",
            "reason": "construction",
            "lat": 29.3344,
            "lon": 48.0537,
            "timestamp": "2026-01-16T10:30:00",
            "duration_hours": 24
        }
        """
        try:
            self.broker.publish_event(DataSource.TRAFFIC, {
                "type": "road_closure",
                **closure_data
            })
            logger.info(f"Ingested road closure: {closure_data.get('closure_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest road closure: {e}")
            return False
    
    def ingest_congestion(self, congestion_data: Dict[str, Any]) -> bool:
        """
        Ingest traffic congestion data
        
        Format:
        {
            "zone": "Salmiya",
            "congestion_level": "high",
            "avg_speed": 15,
            "lat": 29.3344,
            "lon": 48.0537,
            "timestamp": "2026-01-16T10:30:00"
        }
        """
        try:
            self.broker.publish_event(DataSource.TRAFFIC, {
                "type": "congestion",
                **congestion_data
            })
            logger.info(f"Ingested traffic congestion: {congestion_data.get('zone')}")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest traffic congestion: {e}")
            return False
