"""
Data Ingestion API Endpoints
Provides REST API for external systems to push data into Khareetaty
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

from services.ingest_moi import MOIIngestionService
from services.ingest_fire_ems import FireEMSIngestionService
from services.ingest_municipal import MunicipalIngestionService
from services.ingest_traffic import TrafficIngestionService
from services.ingest_iot import IoTIngestionService
from utils.auth import decode_token

router = APIRouter()

# Initialize services
moi_service = MOIIngestionService()
fire_ems_service = FireEMSIngestionService()
municipal_service = MunicipalIngestionService()
traffic_service = TrafficIngestionService()
iot_service = IoTIngestionService()

# Pydantic models
class IncidentData(BaseModel):
    incident_type: str
    governorate: Optional[str] = "unknown"
    zone: Optional[str] = "unknown"
    lat: float
    lon: float
    timestamp: str
    severity: Optional[str] = "medium"
    description: Optional[str] = ""

class FireIncidentData(BaseModel):
    incident_id: str
    fire_type: str
    severity: str
    location: str
    lat: float
    lon: float
    timestamp: str
    units_dispatched: int
    response_time: Optional[int] = None

class TrafficAccidentData(BaseModel):
    accident_id: str
    severity: str
    vehicles_involved: int
    injuries: int
    location: str
    lat: float
    lon: float
    timestamp: str
    road_blocked: bool

class ComplaintData(BaseModel):
    complaint_id: str
    complaint_type: str
    severity: str
    location: str
    lat: float
    lon: float
    timestamp: str
    description: str

class MotionEventData(BaseModel):
    camera_id: str
    location: str
    lat: float
    lon: float
    timestamp: str
    motion_intensity: str
    duration_seconds: int

class CrowdDensityData(BaseModel):
    camera_id: str
    location: str
    lat: float
    lon: float
    timestamp: str
    density_level: str
    estimated_count: int

# MOI Endpoints
@router.post("/moi/incident")
def ingest_moi_incident(data: IncidentData, user=Depends(decode_token)):
    """
    Ingest incident from MOI system
    Requires authentication
    """
    success = moi_service.ingest_incident(data.dict())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to ingest incident")
    return {"status": "success", "message": "Incident ingested"}

# Fire & EMS Endpoints
@router.post("/fire-ems/incident")
def ingest_fire_incident(data: FireIncidentData, user=Depends(decode_token)):
    """
    Ingest fire incident
    Requires authentication
    """
    success = fire_ems_service.ingest_fire_incident(data.dict())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to ingest fire incident")
    return {"status": "success", "message": "Fire incident ingested"}

# Traffic Endpoints
@router.post("/traffic/accident")
def ingest_traffic_accident(data: TrafficAccidentData, user=Depends(decode_token)):
    """
    Ingest traffic accident
    Requires authentication
    """
    success = traffic_service.ingest_accident(data.dict())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to ingest traffic accident")
    return {"status": "success", "message": "Traffic accident ingested"}

# Municipal Endpoints
@router.post("/municipal/complaint")
def ingest_municipal_complaint(data: ComplaintData, user=Depends(decode_token)):
    """
    Ingest municipal complaint
    Requires authentication
    """
    success = municipal_service.ingest_complaint(data.dict())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to ingest complaint")
    return {"status": "success", "message": "Complaint ingested"}

# IoT & CCTV Endpoints
@router.post("/iot/motion")
def ingest_motion_event(data: MotionEventData, user=Depends(decode_token)):
    """
    Ingest motion detection event
    Requires authentication
    """
    success = iot_service.ingest_motion_event(data.dict())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to ingest motion event")
    return {"status": "success", "message": "Motion event ingested"}

@router.post("/iot/crowd-density")
def ingest_crowd_density(data: CrowdDensityData, user=Depends(decode_token)):
    """
    Ingest crowd density data
    Requires authentication
    """
    success = iot_service.ingest_crowd_density(data.dict())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to ingest crowd density")
    return {"status": "success", "message": "Crowd density ingested"}

# Stream monitoring endpoint
@router.get("/streams/status")
def get_streams_status(user=Depends(decode_token)):
    """
    Get status of all data streams
    Requires authentication
    """
    from services.data_broker import get_broker, DataSource
    
    broker = get_broker()
    status = {}
    
    for source in DataSource:
        info = broker.get_stream_info(source)
        status[source.value] = info
    
    return {"status": "success", "streams": status}
