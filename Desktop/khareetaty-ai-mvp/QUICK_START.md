# ⚡ Khareetaty AI - Quick Start Guide

## 🎯 Get Running in 15 Minutes

### Prerequisites
- Python 3.11+
- PostgreSQL 14+ with PostGIS
- Redis (optional for Phase 5)
- macOS/Linux terminal

---

## Step 1: Install Dependencies (2 min)

```bash
cd /Users/bdr.ai/Desktop/khareetaty-ai-mvp

# Install Python packages
pip install -r requirements.txt

# Install additional packages for full functionality
pip install redis scikit-learn prophet twilio
```

---

## Step 2: Setup Database (3 min)

```bash
# Create database
createdb -U bader khareetaty_ai

# Enable PostGIS
psql -U bader -d khareetaty_ai -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# Run migrations
psql -U bader -d khareetaty_ai -f backend/db/migrations.sql
psql -U bader -d khareetaty_ai -f backend/db/interop_migrations.sql
```

---

## Step 3: Configure Environment (2 min)

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Minimum required settings:**
```env
DB_HOST=localhost
DB_NAME=khareetaty_ai
DB_USER=bader
DB_PASSWORD=secret123
JWT_SECRET=your-secret-key-change-this
```

---

## Step 4: Load Sample Data (2 min)

```bash
# Run ETL job to load sample incidents
python automation/etl_job.py

# Verify data loaded
psql -U bader -d khareetaty_ai -c "SELECT COUNT(*) FROM incidents_clean;"
# Should show: 100 rows
```

---

## Step 5: Create Admin User (1 min)

```bash
psql -U bader -d khareetaty_ai << EOF
INSERT INTO system_users (name, email, phone, role)
VALUES ('Bader', 'bader.naser.ai.sa@gmail.com', '+96566338736', 'superadmin');
EOF
```

---

## Step 6: Start Backend Server (1 min)

```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Server running at:** http://localhost:8000

---

## Step 7: Test the System (4 min)

### 7.1 Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### 7.2 Login & Get Token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "bader.naser.ai.sa@gmail.com"}'

# Copy the access_token from response
```

### 7.3 Run Analytics
```bash
# Replace YOUR_TOKEN with the token from step 7.2
TOKEN="YOUR_TOKEN"

curl -X POST http://localhost:8000/analytics/run \
  -H "Authorization: Bearer $TOKEN"

# Expected: {"status": "analytics refreshed"}
```

### 7.4 View Hotspots
```bash
curl http://localhost:8000/analytics/hotspots \
  -H "Authorization: Bearer $TOKEN"

# Shows detected crime hotspots
```

### 7.5 View Forecast
```bash
curl http://localhost:8000/analytics/forecast \
  -H "Authorization: Bearer $TOKEN"

# Shows 7-day predictions
```

### 7.6 Command Dashboard
```bash
curl http://localhost:8000/commands/overview \
  -H "Authorization: Bearer $TOKEN"

# Shows operational overview
```

---

## 🎉 You're Live!

### What You Have Now:
- ✅ FastAPI backend running
- ✅ PostgreSQL with sample data
- ✅ ML models (clustering + forecasting)
- ✅ JWT authentication
- ✅ 50+ API endpoints
- ✅ Automated daily jobs

---

## 👀 Explore the API

**Interactive API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Key Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | Get JWT token |
| `/analytics/run` | POST | Run ML pipeline |
| `/analytics/hotspots` | GET | Get crime hotspots |
| `/analytics/forecast` | GET | Get predictions |
| `/commands/overview` | GET | Dashboard overview |
| `/commands/tactical` | GET | Tactical view |
| `/commands/alert` | POST | Send manual alert |
| `/tasks/assign` | POST | Assign task to team |
| `/tasks/active` | GET | View active tasks |
| `/health` | GET | System health |

---

## 🔧 Common Issues & Solutions

### Issue: "Connection refused" to database
**Solution:**
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL if needed
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux
```

### Issue: "Module not found"
**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: "JWT token invalid"
**Solution:**
```bash
# Get a fresh token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "bader.naser.ai.sa@gmail.com"}'
```

### Issue: "No data in database"
**Solution:**
```bash
# Reload sample data
python automation/etl_job.py
```

---

## 🚀 Next Steps

### 1. Build Dashboard (Recommended)
```bash
# Option A: Streamlit (Quick)
pip install streamlit plotly folium
streamlit run dashboard/app.py

# Option B: React (Production)
npx create-next-app@latest frontend
```

### 2. Enable Real Notifications
```bash
# Sign up for Twilio
# Add to .env:
TWILIO_SID=your_sid
TWILIO_TOKEN=your_token
WHATSAPP_SENDER=whatsapp:+14155238886
```

### 3. Deploy to Production
```bash
# Docker Compose
docker-compose up -d

# Or Kubernetes
kubectl apply -f kubernetes/
```

### 4. Set Up Monitoring
```bash
# High Availability setup with monitoring
docker-compose -f docker-compose.ha.yml up -d

# Access Grafana: http://localhost:3000
# Access Kibana: http://localhost:5601
```

---

## 📚 Documentation

- **Full Guide**: `NEXT_STEPS.md`
- **Implementation Details**: `README_IMPLEMENTATION.md`
- **Deployment Guide**: `DEPLOYMENT.md`
- **Phase 5 Features**: `PHASE5_SUMMARY.md`
- **Project Overview**: `README.md`

---

## 📞 Need Help?

**Check logs:**
```bash
# Backend logs
tail -f backend/logs/app.log

# Database logs
tail -f /usr/local/var/log/postgresql@14.log  # macOS
```

**Test database connection:**
```bash
psql -U bader -d khareetaty_ai -c "SELECT version();"
```

**Restart everything:**
```bash
# Stop backend (Ctrl+C)
# Restart PostgreSQL
brew services restart postgresql
# Start backend again
cd backend && uvicorn app:app --reload
```

---

## ✅ Verification Checklist

- [ ] PostgreSQL running and accessible
- [ ] Database created with PostGIS extension
- [ ] Migrations applied successfully
- [ ] Sample data loaded (100 incidents)
- [ ] Admin user created
- [ ] Backend server running on port 8000
- [ ] Health check returns "healthy"
- [ ] Can login and get JWT token
- [ ] Analytics pipeline runs successfully
- [ ] API documentation accessible at /docs

---

**🎉 Congratulations! Your Khareetaty AI platform is operational!**

The system is now ready to:
- Ingest crime data
- Detect hotspots with ML
- Forecast future incidents
- Send automated alerts
- Manage tasks and teams
- Provide command center intelligence

**Welcome to the future of public safety! 🇰🇼**
