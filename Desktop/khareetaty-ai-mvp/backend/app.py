from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.api import auth, analytics, incidents, commands, ingestion, iot_analytics, patrol, interoperability, geo, alerts
from backend.middleware.auth import require_auth
from services.clustering import compute_hotspots
from services.modeling import predict_trends, predict_by_governorate
from automation.trigger_alerts import trigger_alerts
from config.settings import DATABASE

# Initialize FastAPI app
app = FastAPI(
    title="Khareetaty AI Backend",
    description="Crime Analytics and Prediction System for Kuwait",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
app.include_router(commands.router, prefix="/commands", tags=["Command & Control"])
app.include_router(ingestion.router, prefix="/ingest", tags=["Data Ingestion"])
app.include_router(iot_analytics.router, prefix="/iot", tags=["IoT Analytics"])
app.include_router(patrol.router, prefix="/patrol", tags=["Patrol Allocation"])
app.include_router(interoperability.router, prefix="/api", tags=["Interoperability"])
app.include_router(geo.router, prefix="/geo", tags=["Geographic Data"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])

# Initialize scheduler for automated tasks
scheduler = BackgroundScheduler()

def daily_analytics_job():
    """Run daily analytics pipeline at 2 AM"""
    print("[SCHEDULER] Running daily analytics job...")
    try:
        compute_hotspots()
        predict_trends()
        predict_by_governorate()
        trigger_alerts()
        print("[SCHEDULER] Daily analytics job completed successfully")
    except Exception as e:
        print(f"[SCHEDULER] Daily analytics job failed: {e}")

# Schedule daily job at 2 AM
scheduler.add_job(daily_analytics_job, 'cron', hour=2, minute=0)
scheduler.start()

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("Khareetaty AI Backend starting up...")
    print("Scheduler started for daily analytics at 2:00 AM")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    scheduler.shutdown()
    print("Khareetaty AI Backend shutting down...")

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": "Khareetaty AI Backend",
        "version": "3.0.0",
        "status": "operational",
        "phase": "Phase 5 - Operational Intelligence",
        "endpoints": {
            "auth": "/auth",
            "analytics": "/analytics",
            "geo": "/geo",
            "alerts": "/alerts",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "scheduler": "running" if scheduler.running else "stopped",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status/live", dependencies=[Depends(require_auth)])
def live_status():
    """Live system status with database connectivity check"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=DATABASE.HOST,
            port=DATABASE.PORT,
            dbname=DATABASE.NAME,
            user=DATABASE.USER,
            password=DATABASE.PASSWORD
        )
        
        cur = conn.cursor()
        
        # Get database stats
        cur.execute("""
            SELECT 
                COUNT(*) as total_incidents,
                COUNT(CASE WHEN timestamp >= NOW() - INTERVAL '24 hours' THEN 1 END) as incidents_24h,
                COUNT(CASE WHEN timestamp >= NOW() - INTERVAL '1 hour' THEN 1 END) as incidents_1h
            FROM incidents_clean
        """)
        
        incident_stats = cur.fetchone()
        
        # Get hotspot stats
        cur.execute("""
            SELECT COUNT(*) as active_hotspots
            FROM zones_hotspots
            WHERE last_seen >= NOW() - INTERVAL '24 hours'
        """)
        
        hotspot_stats = cur.fetchone()
        
        # Get alert stats
        cur.execute("""
            SELECT COUNT(*) as alerts_24h
            FROM alerts_log
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        """)
        
        alert_stats = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return {
            "system": "operational",
            "database": {
                "status": "connected",
                "incidents_total": incident_stats[0] if incident_stats else 0,
                "incidents_24h": incident_stats[1] if incident_stats else 0,
                "incidents_1h": incident_stats[2] if incident_stats else 0,
                "hotspots_24h": hotspot_stats[0] if hotspot_stats else 0,
                "alerts_24h": alert_stats[0] if alert_stats else 0
            },
            "scheduler": "running" if scheduler.running else "stopped",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "system": "degraded",
            "database": {
                "status": "disconnected",
                "error": str(e)
            },
            "scheduler": "running" if scheduler.running else "stopped",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
