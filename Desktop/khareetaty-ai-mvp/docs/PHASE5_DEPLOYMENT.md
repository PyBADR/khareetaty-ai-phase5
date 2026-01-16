# Phase 5 Deployment Guide

## Overview

Phase 5 adds operational intelligence capabilities to Khareetaty-AI:
- **API Layer**: RESTful endpoints for geographic data, analytics, and alerts
- **Enhanced Dashboard**: Interactive Streamlit UI with real-time data
- **WhatsApp Alerts**: Automated intelligent notifications via Twilio
- **Scheduler**: Automated pipeline execution every 12 hours
- **Production Ready**: Docker Compose, Nginx, and deployment configs

---

## Prerequisites

### System Requirements
- Docker & Docker Compose
- PostgreSQL 16+ with PostGIS
- Python 3.11+
- 4GB RAM minimum
- 10GB disk space

### External Services
- **Twilio Account** (for WhatsApp alerts)
  - Account SID
  - Auth Token
  - WhatsApp-enabled phone number

---

## Quick Start (Docker)

### 1. Clone and Configure

```bash
cd /Users/bader/Desktop/khareetaty-ai-mvp

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 2. Required Environment Variables

```bash
# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=khareetaty_ai
DB_USER=postgres
DB_PASSWORD=your_secure_password

# Authentication
SECRET_KEY=your-secret-key-change-in-production
AUTH_TOKEN=khareetaty-secure

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886
WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_TO=whatsapp:+96566338736
WHATSAPP_CONTACTS=+96566338736,+96512345678

# Alerts
ALERT_THRESHOLD=10
RUN_INTERVAL_MINUTES=720
```

### 3. Build and Run

```bash
# Build containers
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 4. Initialize Database

```bash
# Run Phase 5 migrations
docker-compose -f docker-compose.prod.yml exec backend python backend/db/apply_phase5_migrations.py

# Load geographic data
docker-compose -f docker-compose.prod.yml exec backend python load_geo_data.py
```

### 5. Access Services

- **Dashboard**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Nginx Proxy**: http://localhost (if enabled)

---

## Manual Deployment (Without Docker)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Database

```bash
# Create database
psql -U postgres -c "CREATE DATABASE khareetaty_ai;"

# Run migrations
psql -U postgres -d khareetaty_ai -f backend/db/geo_migrations.sql
psql -U postgres -d khareetaty_ai -f backend/db/phase5_migrations.sql

# Load geographic data
python load_geo_data.py
```

### 3. Start Backend

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Start Dashboard

```bash
streamlit run dashboard_streamlit/app.py --server.port=8501
```

---

## API Usage

### Authentication

All API requests require Bearer token authentication:

```bash
curl -H "Authorization: Bearer khareetaty-secure" \
     http://localhost:8000/status/live
```

### Key Endpoints

#### System Status
```bash
GET /status/live
```

#### Geographic Data
```bash
GET /geo/options
GET /geo/governorates
GET /geo/districts?governorate=Capital
POST /geo/resolve
  Body: {"lat": 29.3759, "lon": 47.9774}
```

#### Analytics
```bash
POST /analytics/run
```

#### Alerts
```bash
POST /alerts/send
  Body: {"message": "Test", "phone": "+96566338736"}
POST /alerts/trigger-hotspot
GET /alerts/history?limit=50
```

### Postman Collection

Import `docs/POSTMAN_COLLECTION.json` into Postman for complete API testing.

---

## Scheduler Configuration

The automated scheduler runs:
- **Frequency**: Every 12 hours (configurable via `RUN_INTERVAL_MINUTES`)
- **Default Time**: 2:00 AM daily
- **Tasks**:
  1. ETL pipeline (ingest and clean data)
  2. Clustering (detect hotspots)
  3. Forecasting (predict next 24h)
  4. Alerts (send notifications if threshold exceeded)

### Modify Schedule

Edit `backend/main.py`:

```python
scheduler.add_job(
    run_daily_pipeline,
    'cron',
    hour=2,  # Change hour
    minute=0,
    id='daily_pipeline'
)
```

Or use interval-based:

```python
scheduler.add_job(
    run_daily_pipeline,
    'interval',
    minutes=int(os.getenv('RUN_INTERVAL_MINUTES', 720)),
    id='daily_pipeline'
)
```

---

## Dashboard Features

### 1. Map View
- Interactive map with incident markers
- Geographic filters (governorate, district, police zone)
- Hotspot overlays with intensity shading
- Forecast predictions

### 2. Hotspots Tab
- List of active hotspots
- Score distribution chart
- Zone-level statistics
- Last detection timestamp

### 3. Trends Tab
- Time-series analysis
- Per-zone trend lines
- Stacked area charts
- Aggregation options (daily/weekly/monthly)

### 4. Alerts Tab
- Send manual alerts
- View alert history
- Alert statistics
- Trigger analytics pipeline

### 5. KPI Cards
- Total active hotspots
- Most dangerous zone today
- Forecast load (next 24h)
- Alerts sent today

---

## Monitoring & Logs

### Docker Logs

```bash
# Backend logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Dashboard logs
docker-compose -f docker-compose.prod.yml logs -f dashboard

# Database logs
docker-compose -f docker-compose.prod.yml logs -f postgres
```

### Application Logs

Logs are stored in `/app/logs/` (inside containers) or `./logs/` (host):
- `etl.log` - ETL pipeline execution
- `clustering.log` - Hotspot detection
- `alerts.log` - Alert sending
- `api.log` - API requests

### Database Monitoring

```sql
-- Check pipeline runs
SELECT * FROM analytics_summary ORDER BY run_timestamp DESC LIMIT 10;

-- Check alert history
SELECT * FROM alerts_log ORDER BY sent_at DESC LIMIT 20;

-- Check geo resolution success rate
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN resolved THEN 1 ELSE 0 END) as resolved,
    ROUND(100.0 * SUM(CASE WHEN resolved THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM geo_resolution_log;
```

---

## Production Deployment

### Hugging Face Spaces

1. Create new Space (Streamlit)
2. Upload repository
3. Add secrets in Settings:
   - `DB_HOST`, `DB_USER`, `DB_PASSWORD`
   - `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`
   - `AUTH_TOKEN`
4. Deploy

### Render.com

1. Create PostgreSQL database
2. Create Web Service (Docker)
3. Add environment variables
4. Deploy from GitHub

### AWS/GCP/Azure

1. Use `docker-compose.prod.yml`
2. Configure managed PostgreSQL
3. Set up load balancer
4. Configure SSL certificates
5. Enable auto-scaling

---

## Troubleshooting

### Database Connection Failed

```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.prod.yml ps postgres

# Check connection
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -d khareetaty_ai -c "SELECT 1;"
```

### WhatsApp Alerts Not Sending

1. Verify Twilio credentials in `.env`
2. Check Twilio console for errors
3. Ensure WhatsApp number is verified
4. Check `alerts_log` table for error messages

### Geographic Resolution Low Success Rate

1. Verify GeoJSON files loaded: `SELECT COUNT(*) FROM geo_districts;`
2. Check polygon quality (simplified test polygons have ~20% success)
3. Replace with official PACI data for production (85-95% success)

### Scheduler Not Running

```bash
# Check scheduler status in logs
docker-compose -f docker-compose.prod.yml logs backend | grep scheduler

# Manually trigger pipeline
curl -X POST -H "Authorization: Bearer khareetaty-secure" \
     http://localhost:8000/analytics/run
```

---

## Performance Optimization

### Database Indexing

```sql
-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_incidents_timestamp ON incidents_clean(timestamp);
CREATE INDEX IF NOT EXISTS idx_incidents_district ON incidents_clean(district);
CREATE INDEX IF NOT EXISTS idx_hotspots_score ON zones_hotspots(score DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_sent_at ON alerts_log(sent_at DESC);
```

### Caching

Streamlit dashboard uses `@st.cache_data` for:
- Geographic options
- GeoJSON data
- Database queries

Cache TTL: 5 minutes (configurable in `dashboard_streamlit/utils.py`)

### Scaling

- **Backend**: Increase `--workers` in uvicorn command
- **Database**: Use connection pooling (pgbouncer)
- **Dashboard**: Deploy multiple instances behind load balancer

---

## Security Considerations

1. **Change default passwords** in `.env`
2. **Use strong AUTH_TOKEN** (32+ characters)
3. **Enable HTTPS** in production (use Nginx with SSL)
4. **Restrict database access** (firewall rules)
5. **Rotate Twilio credentials** regularly
6. **Enable rate limiting** on API endpoints
7. **Use secrets management** (AWS Secrets Manager, HashiCorp Vault)

---

## Backup & Recovery

### Database Backup

```bash
# Backup
docker-compose -f docker-compose.prod.yml exec postgres \
    pg_dump -U postgres khareetaty_ai > backup_$(date +%Y%m%d).sql

# Restore
docker-compose -f docker-compose.prod.yml exec -T postgres \
    psql -U postgres khareetaty_ai < backup_20260116.sql
```

### Data Backup

```bash
# Backup data directory
tar -czf data_backup_$(date +%Y%m%d).tar.gz data/

# Restore
tar -xzf data_backup_20260116.tar.gz
```

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review documentation: `docs/`
3. Check database status: `/status/live` endpoint
4. Contact: bader@khareetaty-ai.com

---

## Next Steps

1. **Replace test GeoJSON** with official PACI data
2. **Configure production Twilio** account
3. **Set up monitoring** (Prometheus, Grafana)
4. **Enable SSL/HTTPS**
5. **Configure backups** (automated daily)
6. **Load historical data** for better forecasting
7. **Train custom ML models** for prediction
8. **Add user authentication** (OAuth, LDAP)
