"""
Fire & EMS Data Ingestion Service
Handles fire response calls and ambulance deployment data
"""

import logging
from datetime import datetime
from typing import Dict, Any
from services.data_broker import get_broker, DataSource

logger = logging.getLogger(__name__)

class FireEMSIngestionService:
    """
    Ingests data from Fire Department and EMS:
    - Fire response calls
    - Ambulance deployments
    - Emergency medical incidents
    """
    
    def __init__(self):
        self.broker = get_broker()
    
    def ingest_fire_incident(self, fire_data: Dict[str, Any]) -> bool:
        """
        Ingest fire incident
        
        Format:
        {
            "incident_id": "FIRE-2026-001",
            "fire_type": "building",
            "severity": "high",
            "location": "Salmiya",
            "lat": 29.3344,
            "lon": 48.0537,
            "timestamp": "2026-01-16T10:30:00",
            "units_dispatched": 3,
            "response_time": 240
        }
        """
        try:
            self.broker.publish_event(DataSource.FIRE_EMS, {
                "type": "fire_incident",
                **fire_data
            })
            logger.info(f"Ingested fire incident: {fire_data.get('incident_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest fire incident: {e}")
            return False
    
    def ingest_ambulance_deployment(self, ems_data: Dict[str, Any]) -> bool:
        """
        Ingest ambulance deployment
        
        Format:
        {
            "deployment_id": "AMB-2026-001",
            "call_type": "cardiac",
            "priority": "critical",
            "location": "Hawally",
            "lat": 29.3344,
            "lon": 48.0537,
            "timestamp": "2026-01-16T10:30:00",
            "response_time": 180,
            "hospital": "Mubarak Hospital"
        }
        """
        try:
            self.broker.publish_event(DataSource.FIRE_EMS, {
                "type": "ambulance_deployment",
                **ems_data
            })
            logger.info(f"Ingested ambulance deployment: {ems_data.get('deployment_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest ambulance deployment: {e}")
            return False
