from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import psycopg2
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.utils.auth import decode_token

router = APIRouter()

DB_CONN = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME", "khareetaty_ai"),
    "user": os.getenv("DB_USER", "bader"),
    "password": os.getenv("DB_PASSWORD", "secret123")
}

class IncidentCreate(BaseModel):
    incident_type: str
    governorate: str
    zone: str
    lat: float
    lon: float
    description: Optional[str] = ""
    timestamp: Optional[datetime] = None

@router.get("/")
def get_incidents(
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    governorate: Optional[str] = None,
    incident_type: Optional[str] = None,
    user: dict = Depends(decode_token)
):
    """
    Get list of incidents with optional filtering
    """
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    
    query = "SELECT id, incident_type, governorate, zone, lat, lon, timestamp FROM incidents_clean WHERE 1=1"
    params = []
    
    if governorate:
        query += " AND governorate = %s"
        params.append(governorate)
    
    if incident_type:
        query += " AND incident_type = %s"
        params.append(incident_type)
    
    query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    
    incidents = []
    for row in rows:
        incidents.append({
            "id": row[0],
            "incident_type": row[1],
            "governorate": row[2],
            "zone": row[3],
            "lat": row[4],
            "lon": row[5],
            "timestamp": row[6].isoformat() if row[6] else None
        })
    
    return {
        "total": len(incidents),
        "incidents": incidents
    }

@router.post("/")
def create_incident(
    incident: IncidentCreate,
    user: dict = Depends(decode_token)
):
    """
    Create a new incident report
    """
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    
    timestamp = incident.timestamp or datetime.now()
    
    cur.execute("""
        INSERT INTO incidents_raw (incident_type, governorate, zone, lat, lon, timestamp, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        incident.incident_type,
        incident.governorate,
        incident.zone,
        incident.lat,
        incident.lon,
        timestamp,
        incident.description
    ))
    
    incident_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "incident_id": incident_id,
        "message": "Incident created successfully"
    }

@router.get("/hotspots")
def get_hotspots(user: dict = Depends(decode_token)):
    """
    Get current hotspot zones
    """
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT zone, score, predicted, created_at
        FROM zones_hotspots
        WHERE predicted = false
        ORDER BY score DESC
        LIMIT 20
    """)
    
    rows = cur.fetchall()
    conn.close()
    
    hotspots = []
    for row in rows:
        hotspots.append({
            "zone": row[0],
            "score": row[1],
            "predicted": row[2],
            "created_at": row[3].isoformat() if row[3] else None
        })
    
    return {
        "total": len(hotspots),
        "hotspots": hotspots
    }

@router.get("/forecasts")
def get_forecasts(user: dict = Depends(decode_token)):
    """
    Get forecast predictions
    """
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT zone, score, predicted, created_at
        FROM zones_hotspots
        WHERE predicted = true
        ORDER BY created_at DESC
        LIMIT 20
    """)
    
    rows = cur.fetchall()
    conn.close()
    
    forecasts = []
    for row in rows:
        forecasts.append({
            "zone": row[0],
            "score": row[1],
            "predicted": row[2],
            "created_at": row[3].isoformat() if row[3] else None
        })
    
    return {
        "total": len(forecasts),
        "forecasts": forecasts
    }
