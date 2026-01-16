"""
Municipal Data Ingestion Service
Handles complaints, noise violations, and public hazard reports
"""

import logging
from datetime import datetime
from typing import Dict, Any
from services.data_broker import get_broker, DataSource

logger = logging.getLogger(__name__)

class MunicipalIngestionService:
    """
    Ingests data from Municipal services:
    - Noise complaints
    - Street light outages
    - Public hazard reports
    - Infrastructure issues
    """
    
    def __init__(self):
        self.broker = get_broker()
    
    def ingest_complaint(self, complaint_data: Dict[str, Any]) -> bool:
        """
        Ingest municipal complaint
        
        Format:
        {
            "complaint_id": "MUN-2026-001",
            "complaint_type": "noise",
            "severity": "medium",
            "location": "Salmiya",
            "lat": 29.3344,
            "lon": 48.0537,
            "timestamp": "2026-01-16T10:30:00",
            "description": "Loud music after midnight"
        }
        """
        try:
            self.broker.publish_event(DataSource.MUNICIPAL, {
                "type": "complaint",
                **complaint_data
            })
            logger.info(f"Ingested municipal complaint: {complaint_data.get('complaint_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest municipal complaint: {e}")
            return False
    
    def ingest_hazard_report(self, hazard_data: Dict[str, Any]) -> bool:
        """
        Ingest public hazard report
        
        Format:
        {
            "hazard_id": "HAZ-2026-001",
            "hazard_type": "pothole",
            "severity": "high",
            "location": "Hawally",
            "lat": 29.3344,
            "lon": 48.0537,
            "timestamp": "2026-01-16T10:30:00",
            "status": "reported"
        }
        """
        try:
            self.broker.publish_event(DataSource.MUNICIPAL, {
                "type": "hazard_report",
                **hazard_data
            })
            logger.info(f"Ingested hazard report: {hazard_data.get('hazard_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest hazard report: {e}")
            return False
