"""
Patrol Allocation API Endpoints
Provides predictive patrol allocation and resource optimization
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from services.patrol_allocation import PatrolAllocationEngine
from utils.auth import decode_token

router = APIRouter()
patrol_engine = PatrolAllocationEngine()

class TeamAssignment(BaseModel):
    available_teams: List[str]

@router.get("/predict-hotspots")
def predict_hotspots(user=Depends(decode_token)):
    """
    Predict tomorrow's high-risk zones
    Requires authentication
    """
    hotspots = patrol_engine.predict_tomorrows_hotspots()
    return {
        "status": "success",
        "hotspots": hotspots,
        "count": len(hotspots)
    }

@router.get("/recommend-routes")
def recommend_routes(num_teams: int = 5, user=Depends(decode_token)):
    """
    Get recommended patrol routes
    Requires authentication
    """
    if user["role"] not in ("analyst", "superadmin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    routes = patrol_engine.recommend_patrol_routes(num_teams=num_teams)
    return {
        "status": "success",
        "routes": routes,
        "team_count": len(routes)
    }

@router.post("/assign-teams")
def assign_teams(assignment: TeamAssignment, user=Depends(decode_token)):
    """
    Assign teams to high-risk zones
    Requires analyst or superadmin role
    """
    if user["role"] not in ("analyst", "superadmin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    assignments = patrol_engine.assign_teams_to_zones(assignment.available_teams)
    return {
        "status": "success",
        "assignments": assignments,
        "count": len(assignments)
    }

@router.get("/coverage-gaps")
def get_coverage_gaps(user=Depends(decode_token)):
    """
    Detect patrol coverage gaps
    Requires authentication
    """
    gaps = patrol_engine.detect_coverage_gaps()
    return {
        "status": "success",
        "analysis": gaps
    }

@router.get("/team-workload/{team_id}")
def get_team_workload(team_id: str, days: int = 7, user=Depends(decode_token)):
    """
    Check if team is overworked
    Requires authentication
    """
    analysis = patrol_engine.detect_team_overwork(team_id, days)
    return {
        "status": "success",
        "analysis": analysis
    }

@router.get("/optimize-resources")
def optimize_resources(user=Depends(decode_token)):
    """
    Get resource optimization recommendations
    Requires analyst or superadmin role
    """
    if user["role"] not in ("analyst", "superadmin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    optimization = patrol_engine.optimize_resource_distribution()
    return {
        "status": "success",
        "optimization": optimization
    }

@router.get("/report")
def get_patrol_report(user=Depends(decode_token)):
    """
    Generate comprehensive patrol allocation report
    Requires analyst or superadmin role
    """
    if user["role"] not in ("analyst", "superadmin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    report = patrol_engine.generate_patrol_report()
    return {
        "status": "success",
        "report": report
    }
