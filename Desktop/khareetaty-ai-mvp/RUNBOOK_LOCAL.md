# 🚀 KHAREETATY-AI LOCAL EXECUTION RUNBOOK

## Prerequisites

### System Requirements
- **OS**: macOS, Linux, or Windows with WSL
- **Python**: 3.9 or higher
- **PostgreSQL**: 13+ with PostGIS extension
- **RAM**: Minimum 4GB available
- **Disk**: 2GB free space

### Required Software
1. **PostgreSQL with PostGIS**
   - macOS: `brew install postgresql postgis`
   - Ubuntu: `sudo apt-get install postgresql postgresql-contrib postgis`
   - [PostgreSQL Downloads](https://www.postgresql.org/download/)

2. **Python 3.9+**
   - Check version: `python3 --version`
   - [Python Downloads](https://www.python.org/downloads/)

3. **Git** (for cloning repository)
   - [Git Downloads](https://git-scm.com/downloads)

---

## 📋 STEP-BY-STEP SETUP

### Step 1: Clone Repository
```bash
cd ~/Projects
git clone <repository-url>
cd khareetaty-ai-mvp
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Key Dependencies** (from [file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/requirements.txt]):
- FastAPI + Uvicorn (API server)
- SQLAlchemy + psycopg2 (Database)
- Prophet (Forecasting)
- scikit-learn (Clustering)
- Twilio (Notifications)
- python-dotenv (Environment variables)
- passlib + PyJWT (Authentication)

### Step 4: Configure Environment Variables
```bash
cp .env.example .env
```

Edit [file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/.env] with your settings:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=khareetaty_ai
DB_USER=bdr.ai
DB_PASSWORD=secret123

# JWT Authentication
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
SMS_SENDER=+1234567890

# WhatsApp Configuration
WHATSAPP_API_KEY=your_whatsapp_api_key
WHATSAPP_PHONE_ID=your_phone_id

# Alert Thresholds
ALERT_THRESHOLD_HIGH=10
ALERT_THRESHOLD_CRITICAL=20

# Scheduler
SCHEDULER_ENABLED=true
SCHEDULER_HOUR=2
SCHEDULER_MINUTE=0
```

**🔐 Security Note**: Never commit `.env` to version control!

### Step 5: Start PostgreSQL
```bash
# macOS (Homebrew)
brew services start postgresql

# Linux (systemd)
sudo systemctl start postgresql

# Check status
psql --version
```

### Step 6: Initialize Database
```bash
# Run the setup script
chmod +x setup_database.sh
./setup_database.sh
```

This script ([file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/setup_database.sh]):
1. Creates `khareetaty_ai` database
2. Enables PostGIS extension
3. Runs migrations from [file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/backend/db/migrations.sql]
4. Creates default admin user
5. Generates sample incident data

**Manual Alternative**:
```bash
psql -U bdr.ai -d postgres
```
```sql
CREATE DATABASE khareetaty_ai;
\c khareetaty_ai
CREATE EXTENSION postgis;
\i backend/db/migrations.sql
\q
```

Then run:
```bash
python3 src/sample_data_generator.py
```

### Step 7: Verify Database Setup
```bash
psql -U bdr.ai -d khareetaty_ai -c "\dt"
```

Expected tables:
- `incidents_raw`
- `incidents_clean`
- `zones_hotspots`
- `analytics_summary`
- `alerts_log`
- `system_users`

---

## 🎯 RUNNING THE APPLICATION

### Option A: Run Full Pipeline (ETL + Analytics + Alerts)
```bash
python3 main.py
```

This executes ([file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/main.py]):
1. **Data Cleanup** - Removes old records
2. **ETL Pipeline** - Loads and cleans incident data
3. **Clustering** - Detects hotspot zones
4. **Forecasting** - Runs Prophet models
5. **Alert System** - Checks thresholds and sends notifications
6. **Scheduler** - Sets up daily automation

**Expected Output**:
```
2026-01-16 12:00:00 - INFO - Starting data cleanup...
2026-01-16 12:00:01 - INFO - Cleaned up 0 old records
2026-01-16 12:00:01 - INFO - Starting ETL pipeline...
2026-01-16 12:00:05 - INFO - ETL completed: 500 incidents processed
2026-01-16 12:00:05 - INFO - Starting clustering analysis...
2026-01-16 12:00:08 - INFO - Clustering completed: 15 hotspots detected
2026-01-16 12:00:08 - INFO - Starting forecasting models...
2026-01-16 12:00:15 - INFO - Forecasting completed
2026-01-16 12:00:15 - INFO - Checking alert thresholds...
2026-01-16 12:00:16 - INFO - Alerts processed: 3 sent
```

### Option B: Run API Server Only
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**API will be available at**:
- Local: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Option C: Run Individual Services

**ETL Pipeline**:
```bash
python3 automation/etl_job.py
```

**Clustering Analysis**:
```bash
python3 -c "from services.clustering import run_clustering; run_clustering()"
```

**Forecasting**:
```bash
python3 -c "from services.modeling import run_forecasting; run_forecasting()"
```

**Alert System**:
```bash
python3 -c "from services.trigger_alerts import check_and_send_alerts; check_and_send_alerts()"
```

---

## 🌐 ACCESSING THE DASHBOARD

### Start Dashboard Server
```bash
python3 src/dashboard.py
```

**Dashboard URL**: http://localhost:8050

**Features**:
- 🗺️ Interactive map with incident markers
- 📊 Real-time analytics charts
- 🔥 Hotspot zone visualization
- 📈 Forecasting trends
- 🚨 Active alerts panel

---

## 🧪 TESTING THE API

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "2026-01-16T12:00:00"}
```

### 2. User Registration
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "role": "analyst"
  }'
```

### 3. User Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Save the returned `access_token` for authenticated requests.

### 4. Get Incidents (Authenticated)
```bash
curl http://localhost:8000/api/incidents?limit=10 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Get Hotspots
```bash
curl http://localhost:8000/api/hotspots \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Get Analytics Summary
```bash
curl http://localhost:8000/api/analytics/summary \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. Trigger Manual Pipeline Run
```bash
curl -X POST http://localhost:8000/api/pipeline/run \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📱 EXPOSING WITH NGROK (Optional)

### Install ngrok
```bash
brew install ngrok  # macOS
# Or download from https://ngrok.com/download
```

### Authenticate ngrok
```bash
ngrok config add-authtoken YOUR_NGROK_TOKEN
```

### Expose API Server
```bash
ngrok http 8000
```

**You'll get a public URL like**: `https://abc123.ngrok.io`

Update your frontend/mobile app to use this URL.

---

## 🔍 MONITORING & LOGS

### View Application Logs
```bash
tail -f khareetaty.log
```

### Check Database Logs
```bash
# macOS
tail -f /usr/local/var/log/postgresql@14.log

# Linux
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### Monitor Database Activity
```bash
psql -U bdr.ai -d khareetaty_ai
```
```sql
-- Active connections
SELECT * FROM pg_stat_activity;

-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Recent incidents
SELECT * FROM incidents_clean ORDER BY incident_date DESC LIMIT 10;

-- Active hotspots
SELECT * FROM zones_hotspots WHERE severity IN ('HIGH', 'CRITICAL');

-- Recent alerts
SELECT * FROM alerts_log ORDER BY created_at DESC LIMIT 10;
```

---

## 🛠️ TROUBLESHOOTING

### Issue: Database Connection Failed
**Error**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:
1. Check PostgreSQL is running: `brew services list` or `systemctl status postgresql`
2. Verify credentials in `.env` match your PostgreSQL user
3. Test connection: `psql -U bdr.ai -d khareetaty_ai`
4. Check PostgreSQL is listening: `lsof -i :5432`

### Issue: Module Not Found
**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Port Already in Use
**Error**: `Address already in use: 8000`

**Solution**:
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 $(lsof -ti:8000)

# Or use a different port
uvicorn app:app --port 8001
```

### Issue: PostGIS Extension Not Found
**Error**: `ERROR: could not open extension control file`

**Solution**:
```bash
# macOS
brew install postgis

# Ubuntu
sudo apt-get install postgresql-13-postgis-3

# Then reconnect and create extension
psql -U bdr.ai -d khareetaty_ai -c "CREATE EXTENSION postgis;"
```

### Issue: Twilio Authentication Failed
**Error**: `TwilioRestException: Unable to create record`

**Solution**:
1. Verify `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` in `.env`
2. Check phone number format: `+1234567890`
3. Verify Twilio account is active: [Twilio Console](https://www.twilio.com/console)

### Issue: Prophet Model Fails
**Error**: `ValueError: Dataframe has less than 2 non-NaN rows`

**Solution**:
- Ensure you have enough historical data (minimum 2 days)
- Run sample data generator: `python3 src/sample_data_generator.py`

---

## 📊 PERFORMANCE OPTIMIZATION

### Database Indexing
Indexes are automatically created by [file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/backend/db/migrations.sql]:
- `incidents_clean(incident_date)`
- `incidents_clean(zone_name)`
- `zones_hotspots(severity)`
- `alerts_log(created_at)`

### Caching (Future Enhancement)
Consider adding Redis for:
- API response caching
- Session management
- Real-time analytics

### Scaling Considerations
- Use connection pooling (SQLAlchemy already configured)
- Add read replicas for PostgreSQL
- Deploy API with Gunicorn + multiple workers
- Use Celery for background tasks

---

## 🔄 DAILY OPERATIONS

### Automated Scheduler
The scheduler runs daily at 2:00 AM (configurable in `.env`):
```python
# Configured in main.py
schedule.every().day.at("02:00").do(run_full_pipeline)
```

### Manual Pipeline Execution
```bash
# Run full pipeline
python3 main.py

# Or via API
curl -X POST http://localhost:8000/api/pipeline/run \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Backup Database
```bash
# Create backup
pg_dump -U bdr.ai khareetaty_ai > backup_$(date +%Y%m%d).sql

# Restore backup
psql -U bdr.ai khareetaty_ai < backup_20260116.sql
```

---

## 📚 ADDITIONAL RESOURCES

- **Project Documentation**: [file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/README.md]
- **Gap Report**: [file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/GAP_REPORT.md]
- **Action Log**: [file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/ACTION_LOG.md]
- **API Documentation**: http://localhost:8000/docs (when server is running)
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Prophet Docs**: https://facebook.github.io/prophet/
- **PostGIS Docs**: https://postgis.net/documentation/

---

## ✅ SUCCESS CHECKLIST

- [ ] PostgreSQL running and accessible
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] `.env` file configured
- [ ] Database created with PostGIS
- [ ] Migrations applied successfully
- [ ] Sample data generated
- [ ] Pipeline runs without errors
- [ ] API server starts successfully
- [ ] Dashboard accessible
- [ ] Authentication working
- [ ] Alerts being sent

---

**🎉 You're ready to go! The khareetaty-ai platform is now running locally.**

For Docker deployment, see [file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/RUNBOOK_DOCKER.md]