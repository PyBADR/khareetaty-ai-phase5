"""
IoT Analytics API Endpoints
Provides analytics and insights from IoT sensor and CCTV metadata
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
from services.iot_processor import IoTProcessor
from utils.auth import decode_token

router = APIRouter()
iot_processor = IoTProcessor()

@router.get("/insights")
def get_iot_insights(user=Depends(decode_token)):
    """
    Get current IoT insights and anomalies
    Requires authentication
    """
    insights = iot_processor.generate_iot_insights()
    return {
        "status": "success",
        "insights": insights,
        "count": len(insights)
    }

@router.get("/risk-score/{zone}")
def get_zone_iot_risk(zone: str, user=Depends(decode_token)):
    """
    Get IoT-based risk score for a zone
    Requires authentication
    """
    risk_score = iot_processor.aggregate_iot_risk_score(zone)
    return {
        "status": "success",
        "zone": zone,
        "iot_risk_score": risk_score
    }

@router.get("/crowd-correlation/{location}")
def get_crowd_correlation(location: str, density_level: str = "high", user=Depends(decode_token)):
    """
    Get crowd density correlation with incidents
    Requires authentication
    """
    correlation = iot_processor.process_crowd_density_correlation(location, density_level)
    return {
        "status": "success",
        "correlation": correlation
    }
