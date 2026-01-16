"""
Interoperability API Endpoints
Provides standardized APIs for external government systems
"""

from fastapi import APIRouter, HTTPException, Header, Request, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

from services.interop_manager import InteroperabilityManager
from services.ingest_moi import MOIIngestionService
from services.ingest_fire_ems import FireEMSIngestionService
from services.ingest_traffic import TrafficIngestionService
from services.ingest_municipal import MunicipalIngestionService
from utils.auth import decode_token

logger = logging.getLogger(__name__)

router = APIRouter()
interop_manager = InteroperabilityManager()

# Ingestion services
moi_service = MOIIngestionService()
fire_service = FireEMSIngestionService()
traffic_service = TrafficIngestionService()
municipal_service = MunicipalIngestionService()

# Models
class APIKeyRequest(BaseModel):
    service_name: str
    permissions: str = "read"

class WebhookSubscription(BaseModel):
    service_name: str
    webhook_url: str
    event_types: List[str]
    secret: str

class StandardIncident(BaseModel):
    incident_type: str
    governorate: Optional[str] = "unknown"
    zone: Optional[str] = "unknown"
    lat: float
    lon: float
    timestamp: str
    severity: Optional[str] = "medium"
    description: Optional[str] = ""

# Dependency for API key authentication
async def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from header"""
    service_info = interop_manager.validate_api_key(x_api_key)
    
    if not service_info:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check rate limit
    if not interop_manager.check_rate_limit(service_info["service_name"]):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return service_info

# ============================================
# API Key Management (Admin only)
# ============================================

@router.post("/admin/api-keys/generate")
def generate_api_key(request: APIKeyRequest, user=Depends(decode_token)):
    """
    Generate API key for external service
    Requires superadmin role
    """
    if user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    api_key = interop_manager.generate_api_key(
        request.service_name,
        request.permissions
    )
    
    if not api_key:
        raise HTTPException(status_code=500, detail="Failed to generate API key")
    
    return {
        "status": "success",
        "service_name": request.service_name,
        "api_key": api_key,
        "permissions": request.permissions
    }

@router.delete("/admin/api-keys/{service_name}")
def revoke_api_key(service_name: str, user=Depends(decode_token)):
    """
    Revoke API key for a service
    Requires superadmin role
    """
    if user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    success = interop_manager.revoke_api_key(service_name)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to revoke API key")
    
    return {
        "status": "success",
        "message": f"API key revoked for {service_name}"
    }

@router.get("/admin/api-keys/stats/{service_name}")
def get_api_stats(service_name: str, days: int = 7, user=Depends(decode_token)):
    """
    Get API usage statistics for a service
    Requires analyst or superadmin role
    """
    if user["role"] not in ("analyst", "superadmin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    stats = interop_manager.get_service_statistics(service_name, days)
    
    return {
        "status": "success",
        "statistics": stats
    }

# ============================================
# Inbound APIs (External systems push data)
# ============================================

@router.post("/external/incident")
async def receive_incident(incident: StandardIncident, request: Request, service_info=Depends(verify_api_key)):
    """
    Receive incident from external system
    Requires valid API key with write permissions
    """
    if service_info["permissions"] not in ("write", "admin"):
        raise HTTPException(status_code=403, detail="Write permission required")
    
    # Log request
    interop_manager.log_api_request(
        service_info["service_name"],
        "/external/incident",
        "POST",
        200
    )
    
    # Ingest incident
    success = moi_service.ingest_incident(incident.dict())
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to ingest incident")
    
    return {
        "status": "success",
        "message": "Incident received and processed",
        "incident_type": incident.incident_type
    }

@router.post("/external/batch-incidents")
async def receive_batch_incidents(incidents: List[StandardIncident], request: Request, service_info=Depends(verify_api_key)):
    """
    Receive batch of incidents from external system
    Requires valid API key with write permissions
    """
    if service_info["permissions"] not in ("write", "admin"):
        raise HTTPException(status_code=403, detail="Write permission required")
    
    # Log request
    interop_manager.log_api_request(
        service_info["service_name"],
        "/external/batch-incidents",
        "POST",
        200
    )
    
    # Ingest all incidents
    success_count = 0
    failed_count = 0
    
    for incident in incidents:
        if moi_service.ingest_incident(incident.dict()):
            success_count += 1
        else:
            failed_count += 1
    
    return {
        "status": "success",
        "message": f"Processed {len(incidents)} incidents",
        "successful": success_count,
        "failed": failed_count
    }

# ============================================
# Outbound APIs (External systems pull data)
# ============================================

@router.get("/external/hotspots")
async def get_hotspots(request: Request, service_info=Depends(verify_api_key)):
    """
    Get current hotspots
    Requires valid API key with read permissions
    """
    # Log request
    interop_manager.log_api_request(
        service_info["service_name"],
        "/external/hotspots",
        "GET",
        200
    )
    
    import psycopg2
    from services.interop_manager import DB_CONN
    
    try:
        conn = psycopg2.connect(**DB_CONN)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT zone, score, predicted, created_at
            FROM zones_hotspots
            WHERE predicted = false
            ORDER BY score DESC
            LIMIT 20
        """)
        
        hotspots = [{
            "zone": row[0],
            "risk_score": float(row[1]),
            "predicted": row[2],
            "detected_at": row[3].isoformat()
        } for row in cur.fetchall()]
        
        conn.close()
        
        return {
            "status": "success",
            "hotspots": hotspots,
            "count": len(hotspots)
        }
        
    except Exception as e:
        logger.error(f"Failed to get hotspots: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve hotspots")

@router.get("/external/alerts")
async def get_alerts(request: Request, hours: int = 24, service_info=Depends(verify_api_key)):
    """
    Get recent alerts
    Requires valid API key with read permissions
    """
    # Log request
    interop_manager.log_api_request(
        service_info["service_name"],
        "/external/alerts",
        "GET",
        200
    )
    
    import psycopg2
    from services.interop_manager import DB_CONN
    
    try:
        conn = psycopg2.connect(**DB_CONN)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT zone, severity, message, created_at
            FROM alerts
            WHERE created_at > NOW() - INTERVAL '%s hours'
            ORDER BY created_at DESC
        """, (hours,))
        
        alerts = [{
            "zone": row[0],
            "severity": row[1],
            "message": row[2],
            "timestamp": row[3].isoformat()
        } for row in cur.fetchall()]
        
        conn.close()
        
        return {
            "status": "success",
            "alerts": alerts,
            "count": len(alerts),
            "hours": hours
        }
        
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")

@router.get("/external/incidents")
async def get_incidents(request: Request, governorate: Optional[str] = None, hours: int = 24, service_info=Depends(verify_api_key)):
    """
    Get recent incidents
    Requires valid API key with read permissions
    """
    # Log request
    interop_manager.log_api_request(
        service_info["service_name"],
        "/external/incidents",
        "GET",
        200
    )
    
    import psycopg2
    from services.interop_manager import DB_CONN
    
    try:
        conn = psycopg2.connect(**DB_CONN)
        cur = conn.cursor()
        
        if governorate:
            cur.execute("""
                SELECT incident_type, governorate, zone, lat, lon, timestamp
                FROM incidents_clean
                WHERE governorate = %s
                AND timestamp > NOW() - INTERVAL '%s hours'
                ORDER BY timestamp DESC
                LIMIT 100
            """, (governorate, hours))
        else:
            cur.execute("""
                SELECT incident_type, governorate, zone, lat, lon, timestamp
                FROM incidents_clean
                WHERE timestamp > NOW() - INTERVAL '%s hours'
                ORDER BY timestamp DESC
                LIMIT 100
            """, (hours,))
        
        incidents = [{
            "incident_type": row[0],
            "governorate": row[1],
            "zone": row[2],
            "lat": float(row[3]),
            "lon": float(row[4]),
            "timestamp": row[5].isoformat()
        } for row in cur.fetchall()]
        
        conn.close()
        
        return {
            "status": "success",
            "incidents": incidents,
            "count": len(incidents),
            "governorate": governorate,
            "hours": hours
        }
        
    except Exception as e:
        logger.error(f"Failed to get incidents: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve incidents")

# ============================================
# Health & Status
# ============================================

@router.get("/external/health")
async def health_check(service_info=Depends(verify_api_key)):
    """
    Health check endpoint for external systems
    """
    return {
        "status": "healthy",
        "service": "Khareetaty AI Interoperability API",
        "version": "1.0",
        "authenticated_as": service_info["service_name"]
    }
