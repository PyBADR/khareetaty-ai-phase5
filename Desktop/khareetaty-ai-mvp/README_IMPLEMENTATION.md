# Khareetaty AI - Implementation Guide

## 🎯 System Overview

Khareetaty AI is a comprehensive crime analytics and prediction platform for Kuwait, featuring:

- **ETL Pipeline**: Automated data ingestion and processing
- **ML Analytics**: DBSCAN clustering for hotspot detection
- **Forecasting**: Prophet-based time series predictions
- **Alert System**: Real-time notifications via WhatsApp/SMS
- **REST API**: FastAPI backend with JWT authentication
- **Role-Based Access**: Superadmin, Analyst, and Viewer roles

## 📁 Project Structure

```
khareetaty-ai-mvp/
├── automation/
│   ├── etl_job.py              # ETL pipeline with validation
│   └── trigger_alerts.py        # Alert triggering system
├── backend/
│   ├── api/
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── analytics.py        # ML pipeline endpoints
│   │   └── incidents.py        # Incident CRUD endpoints
│   ├── db/
│   │   └── migrations.sql      # Database schema
│   ├── utils/
│   │   └── auth.py             # JWT utilities
│   └── app.py                  # FastAPI application
├── services/
│   ├── clustering.py           # DBSCAN hotspot detection
│   ├── modeling.py             # Prophet forecasting
│   └── notifications.py        # Multi-channel notifications
├── data/
│   ├── staging/                # CSV files for ingestion
│   └── archive/                # Processed files
├── requirements.txt            # Python dependencies
└── main.py                     # Pipeline orchestrator
```

## 🚀 Quick Start

### 1. Database Setup

```bash
# Install PostgreSQL with PostGIS
brew install postgresql postgis  # macOS

# Start PostgreSQL
brew services start postgresql

# Create database
psql postgres
CREATE DATABASE khareetaty_ai;
\c khareetaty_ai
CREATE EXTENSION postgis;

# Run migrations
psql -d khareetaty_ai -f backend/db/migrations.sql
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create `.env` file:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=khareetaty_ai
DB_USER=bader
DB_PASSWORD=secret123

# JWT
JWT_SECRET=your-secret-key-change-in-production

# Twilio (for WhatsApp/SMS)
TWILIO_SID=your_twilio_account_sid
TWILIO_TOKEN=your_twilio_auth_token
WHATSAPP_SENDER=whatsapp:+14155238886
SMS_SENDER=+1234567890

# Alerts
ALERT_THRESHOLD=10
ADMIN_PHONE=+96566338736
```

## 📊 Running the System

### Phase 1: ETL Pipeline

```bash
# Load CSV data and clean
python automation/etl_job.py
```

### Phase 2: Analytics & ML

```bash
# Run clustering
python services/clustering.py

# Run forecasting
python services/modeling.py

# Trigger alerts
python automation/trigger_alerts.py
```

### Phase 3: Start API Server

```bash
# Start FastAPI backend
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# API will be available at:
# http://localhost:8000
# Docs: http://localhost:8000/docs
```

## 🔐 Authentication

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "bader.naser.ai.sa@gmail.com", "password": "admin123"}'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Bader",
    "email": "bader.naser.ai.sa@gmail.com",
    "role": "superadmin"
  }
}
```

### Using Token

```bash
curl -X POST http://localhost:8000/analytics/run \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📡 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### Analytics (Requires: analyst/superadmin)
- `POST /analytics/run` - Run full analytics pipeline
- `POST /analytics/clustering` - Run clustering only
- `POST /analytics/forecasting` - Run forecasting only
- `GET /analytics/status` - Get analytics status

### Incidents (Requires: authentication)
- `GET /incidents/` - List incidents (with filters)
- `POST /incidents/` - Create new incident
- `GET /incidents/hotspots` - Get current hotspots
- `GET /incidents/forecasts` - Get predictions

## 🤖 Automated Scheduling

The FastAPI backend includes APScheduler that runs daily at 2 AM:

1. Compute hotspots (DBSCAN clustering)
2. Generate forecasts (Prophet)
3. Trigger alerts (if thresholds exceeded)

To modify schedule, edit `backend/app.py`:

```python
scheduler.add_job(daily_analytics_job, 'cron', hour=2, minute=0)
```

## 🎭 User Roles

### Superadmin
- Full system access
- Run analytics pipelines
- Manage users
- Receive all alerts

### Analyst
- Run analytics pipelines
- View all data
- Create incidents
- Receive alerts

### Viewer
- View incidents
- View hotspots
- View forecasts
- Read-only access

## 📈 ML Models

### DBSCAN Clustering
- **Purpose**: Detect crime hotspots
- **Parameters**: 
  - `eps=0.02` (~2.2km radius)
  - `min_samples=5`
- **Output**: Cluster zones with density scores

### Prophet Forecasting
- **Purpose**: Predict future incident trends
- **Features**: 
  - Daily/weekly seasonality
  - 7-day forecast horizon
  - Governorate-level predictions
- **Output**: Predicted incident counts

## 🚨 Alert System

### Trigger Conditions
- Hotspot score > threshold (default: 10)
- Multiple high-risk zones detected
- Unusual spike in incidents

### Notification Channels
1. **WhatsApp** (via Twilio)
2. **SMS** (via Twilio)
3. **Email** (via SMTP)

### Alert Routing
- Superadmins: All alerts
- Analysts: High-priority alerts
- Zone-based routing (future)

## 🔧 Configuration

### Alert Threshold
```bash
export ALERT_THRESHOLD=15  # Adjust sensitivity
```

### Clustering Parameters
Edit `services/clustering.py`:
```python
model = DBSCAN(eps=0.02, min_samples=5)
```

### Forecast Period
Edit `services/modeling.py`:
```python
future = m.make_future_dataframe(periods=7)  # Change days
```

## 📊 Data Format

### CSV Input Format
```csv
incident_type,governorate,zone,lat,lon,timestamp,description
theft,Capital,Shuwaikh,29.3375,47.9583,2026-01-10T14:30:00,Vehicle theft
```

### Required Fields
- `incident_type`: Type of incident
- `lat`: Latitude (28.5-30.1 for Kuwait)
- `lon`: Longitude (46.5-48.5 for Kuwait)
- `timestamp`: ISO format datetime

### Optional Fields
- `governorate`: Kuwait governorate
- `zone`: Specific zone/area
- `description`: Incident details

## 🐳 Docker Deployment (Future)

```yaml
version: '3.8'
services:
  postgres:
    image: postgis/postgis:14-3.2
    environment:
      POSTGRES_DB: khareetaty_ai
      POSTGRES_USER: bader
      POSTGRES_PASSWORD: secret123
    ports:
      - "5432:5432"
  
  backend:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    environment:
      DB_HOST: postgres
```

## 📝 Testing

### Test ETL
```bash
python automation/etl_job.py
```

### Test Analytics
```bash
python services/clustering.py
python services/modeling.py
```

### Test API
```bash
# Health check
curl http://localhost:8000/health

# Run analytics (with auth)
curl -X POST http://localhost:8000/analytics/run \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🎯 Next Steps (Phase 4+)

### Phase 4: Command & Control
- [ ] Task assignment system
- [ ] Escalation logic
- [ ] Audit logging
- [ ] Multi-channel notifications
- [ ] Decision automation

### Phase 5: National Grid
- [ ] Multi-agency data ingestion
- [ ] IoT/CCTV integration
- [ ] Predictive patrol allocation
- [ ] High availability setup
- [ ] Real-time WebSocket updates

## 🆘 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
psql -d khareetaty_ai -c "SELECT 1;"

# Verify PostGIS extension
psql -d khareetaty_ai -c "SELECT PostGIS_version();"
```

### Import Errors
```bash
# Ensure all dependencies installed
pip install -r requirements.txt

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Alert Not Sending
```bash
# Test mode (no Twilio credentials)
# Will print to console instead
python automation/trigger_alerts.py
```

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Prophet Documentation](https://facebook.github.io/prophet/)
- [PostGIS Documentation](https://postgis.net/documentation/)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)

## 👥 Team

**Project Lead**: Bader Naser  
**Email**: bader.naser.ai.sa@gmail.com  
**Phone**: +965 66338736

---

**Status**: Phase 3 Complete ✅  
**Next Milestone**: Command & Control Features
