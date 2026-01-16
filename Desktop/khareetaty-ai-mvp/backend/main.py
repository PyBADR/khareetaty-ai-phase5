from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from services.clustering import compute_hotspots
from services.modeling import predict_trends, predict_by_governorate
from automation.trigger_alerts import trigger_alerts
import uvicorn
import os

app = FastAPI(title="Khareetaty AI Backend")

# Import routers
from api.analytics import router as analytics_router
from api.auth import router as auth_router
from api.geo import router as geo_router
from api.alerts import router as alerts_router

# Register routers
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(geo_router, prefix="/geo", tags=["geographic"])
app.include_router(alerts_router, prefix="/alerts", tags=["alerts"])

# Set up background scheduler for automated jobs
scheduler = BackgroundScheduler()

def daily_jobs():
    """Run daily analytics and alerting jobs"""
    print("Running daily analytics jobs...")
    compute_hotspots()
    predict_trends()
    predict_by_governorate()
    trigger_alerts()
    print("Daily jobs completed.")

# Schedule jobs to run every night at 2 AM
scheduler.add_job(daily_jobs, 'cron', hour=2)

# Start scheduler
scheduler.start()

@app.on_event("startup")
def startup_event():
    print("Starting Khareetaty AI Backend...")
    print("Scheduler started, daily jobs scheduled for 2 AM")

@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down Khareetaty AI Backend...")
    scheduler.shutdown()

# Health check endpoints
@app.get("/health")
@app.get("/health/live")
def health_live():
    """Liveness probe - checks if the application is running"""
    return {"status": "ok", "service": "khareetaty-ai-backend", "version": "1.0.0"}

@app.get("/health/ready")
def health_ready():
    """Readiness probe - checks if the application is ready to serve traffic"""
    from db.connection import get_db_connection
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"status": "ready", "database": "connected", "scheduler": "running"}
    except Exception as e:
        return {"status": "not_ready", "database": "disconnected", "error": str(e)}

@app.get("/")
def read_root():
    return {
        "service": "Khareetaty AI Backend",
        "version": "1.0.0",
        "status": "running",
        "scheduled_jobs": {
            "daily_analytics": "runs at 2 AM",
            "clustering": "detects hotspots",
            "forecasting": "predicts trends",
            "alerts": "triggers notifications"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "operational",
            "scheduler": "active",
            "analytics": "available"
        }
    }

@app.get("/status/live")
def get_live_status():
    """Get live system status including pipeline, database, and services"""
    import psycopg2
    from datetime import datetime
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "system": "operational",
        "services": {},
        "database": {},
        "pipeline": {}
    }
    
    # Check database connection
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", 5432),
            dbname=os.getenv("DB_NAME", "khareetaty_ai"),
            user=os.getenv("DB_USER", "bdr.ai"),
            password=os.getenv("DB_PASSWORD", "secret123")
        )
        cur = conn.cursor()
        
        # Get incident counts
        cur.execute("SELECT COUNT(*) FROM incidents_clean")
        incident_count = cur.fetchone()[0]
        
        # Get hotspot counts
        cur.execute("SELECT COUNT(*) FROM zones_hotspots WHERE created_at >= NOW() - INTERVAL '24 hours'")
        hotspot_count = cur.fetchone()[0]
        
        # Get alert counts
        try:
            cur.execute("SELECT COUNT(*) FROM alerts_log WHERE sent_at >= NOW() - INTERVAL '24 hours'")
            alert_count = cur.fetchone()[0]
        except:
            alert_count = 0
        
        cur.close()
        conn.close()
        
        status["database"] = {
            "status": "connected",
            "incidents_total": incident_count,
            "hotspots_24h": hotspot_count,
            "alerts_24h": alert_count
        }
    except Exception as e:
        status["database"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check services
    status["services"] = {
        "api": "operational",
        "scheduler": "active" if scheduler.running else "stopped",
        "analytics": "available",
        "geo_lookup": "available",
        "alerts": "available"
    }
    
    # Pipeline status
    status["pipeline"] = {
        "etl": "scheduled",
        "clustering": "scheduled",
        "forecasting": "scheduled",
        "next_run": "2:00 AM daily"
    }
    
    return status

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )