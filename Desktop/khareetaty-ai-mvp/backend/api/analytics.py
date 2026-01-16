from fastapi import APIRouter, Depends, HTTPException
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.clustering import compute_hotspots
from services.modeling import predict_trends, predict_by_governorate
from backend.utils.auth import decode_token, require_role

router = APIRouter()

@router.post("/run")
def run_analytics_pipeline(user: dict = Depends(require_role(["analyst", "superadmin"]))):
    """Run the complete analytics pipeline: clustering and forecasting
    
    Requires: analyst or superadmin role
    """
    try:
        compute_hotspots()
        predict_trends()
        predict_by_governorate()
        return {
            "status": "success",
            "message": "Analytics pipeline completed successfully",
            "executed_by": user["email"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics pipeline failed: {str(e)}")

@router.post("/clustering")
def run_clustering(user: dict = Depends(require_role(["analyst", "superadmin"]))):
    """Run only the clustering algorithm
    
    Requires: analyst or superadmin role
    """
    try:
        compute_hotspots()
        return {
            "status": "success",
            "message": "Clustering analysis completed",
            "executed_by": user["email"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clustering failed: {str(e)}")

@router.post("/forecasting")
def run_forecasting(user: dict = Depends(require_role(["analyst", "superadmin"]))):
    """Run only the forecasting algorithm
    
    Requires: analyst or superadmin role
    """
    try:
        predict_trends()
        predict_by_governorate()
        return {
            "status": "success",
            "message": "Forecasting analysis completed",
            "executed_by": user["email"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting failed: {str(e)}")

@router.get("/status")
def get_analytics_status():
    """Get current status of analytics"""
    return {
        "status": "active",
        "services": {
            "clustering": "available",
            "forecasting": "available",
            "hotspot_detection": "enabled"
        }
    }