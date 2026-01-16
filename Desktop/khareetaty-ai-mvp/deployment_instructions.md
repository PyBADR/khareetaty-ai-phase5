# 🚀 Khareetaty-AI Geographic Enhancement - Deployment Instructions

**Version:** 3.0 (Geographic-Aware)  
**Target Environment:** Production  
**Last Updated:** 2026-01-16

## 📋 Pre-Deployment Checklist

### System Requirements
- [ ] Python 3.11+
- [ ] PostgreSQL 14+ with PostGIS extension
- [ ] 4GB+ RAM (8GB recommended)
- [ ] 20GB+ disk space
- [ ] Ubuntu 20.04+ or macOS 12+

### Dependencies
- [ ] shapely>=2.0.0
- [ ] geojson>=3.0.0
- [ ] rtree>=1.0.0
- [ ] All existing requirements.txt packages

### Access & Credentials
- [ ] Database admin credentials
- [ ] WhatsApp Business API credentials (or Twilio)
- [ ] Server SSH access
- [ ] Git repository access

## 🔧 Deployment Steps

### Step 1: Backup Current System

```bash
# 1.1 Backup database
pg_dump -U bdr.ai khareetaty_ai > backup_pre_geo_$(date +%Y%m%d_%H%M%S).sql

# 1.2 Backup application code
cd /path/to/khareetaty-ai-mvp
tar -czf ../khareetaty_backup_$(date +%Y%m%d).tar.gz .

# 1.3 Verify backups
ls -lh ../khareetaty_backup_*.tar.gz
ls -lh backup_pre_geo_*.sql
```

### Step 2: Pull Latest Code

```bash
# 2.1 Fetch updates
git fetch origin

# 2.2 Create deployment branch
git checkout -b deploy/geo-enhancement-v3.0

# 2.3 Pull geographic enhancement changes
git pull origin feature/geo-enhancement

# 2.4 Verify new files
ls -lh data/geo/kuwait/
ls -lh backend/services/geo_lookup.py
ls -lh backend/db/geo_migrations.sql
```

### Step 3: Install Dependencies

```bash
# 3.1 Activate virtual environment
source venv/bin/activate

# 3.2 Upgrade pip
pip install --upgrade pip

# 3.3 Install new dependencies
pip install shapely>=2.0.0 geojson>=3.0.0 rtree>=1.0.0

# 3.4 Verify installation
python -c "from shapely.geometry import Point; print('Shapely OK')"
python -c "import geojson; print('GeoJSON OK')"
python -c "import rtree; print('Rtree OK')"

# 3.5 Install all requirements (ensure no conflicts)
pip install -r requirements.txt

# 3.6 Freeze current environment
pip freeze > requirements_deployed.txt
```

### Step 4: Database Migration

```bash
# 4.1 Test migration on backup (optional but recommended)
createdb -U bdr.ai khareetaty_ai_test
pg_restore -U bdr.ai -d khareetaty_ai_test backup_pre_geo_*.sql
psql -U bdr.ai -d khareetaty_ai_test -f backend/db/geo_migrations.sql

# 4.2 Apply migration to production
psql -U bdr.ai -d khareetaty_ai -f backend/db/geo_migrations.sql

# 4.3 Verify tables created
psql -U bdr.ai -d khareetaty_ai -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_name LIKE 'geo_%'
ORDER BY table_name;
"

# Expected output:
# geo_blocks
# geo_districts
# geo_governorates
# geo_police_zones
# geo_resolution_log

# 4.4 Verify incidents_clean updated
psql -U bdr.ai -d khareetaty_ai -c "\d incidents_clean" | grep -E "district|block|police_zone"

# Expected output:
# district        | character varying(100) |
# block           | character varying(50)  |
# police_zone     | character varying(100) |
```

### Step 5: Load Geographic Data

```bash
# 5.1 Create data loading script
cat > load_geo_data.py << 'EOF'
import json
import psycopg2
from psycopg2.extras import execute_values
import os

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'khareetaty_ai'),
    'user': os.getenv('DB_USER', 'bdr.ai'),
    'password': os.getenv('DB_PASSWORD', 'secret123'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def load_geojson_to_table(filepath, table_name, conn):
    """Load GeoJSON file into database table."""
    with open(filepath) as f:
        data = json.load(f)
    
    cur = conn.cursor()
    
    if table_name == 'geo_governorates':
        values = [(
            f['properties']['id'],
            f['properties']['name_en'],
            f['properties']['name_ar'],
            json.dumps(f['geometry'])
        ) for f in data['features']]
        
        execute_values(cur, f'''
            INSERT INTO {table_name} (id, name_en, name_ar, geometry)
            VALUES %s ON CONFLICT (id) DO UPDATE SET
                name_en = EXCLUDED.name_en,
                name_ar = EXCLUDED.name_ar,
                geometry = EXCLUDED.geometry
        ''', values)
        
    elif table_name == 'geo_districts':
        values = [(
            f['properties']['id'],
            f['properties']['name_en'],
            f['properties']['name_ar'],
            f['properties']['governorate_id'],
            json.dumps(f['geometry'])
        ) for f in data['features']]
        
        execute_values(cur, f'''
            INSERT INTO {table_name} (id, name_en, name_ar, governorate_id, geometry)
            VALUES %s ON CONFLICT (id) DO UPDATE SET
                name_en = EXCLUDED.name_en,
                name_ar = EXCLUDED.name_ar,
                governorate_id = EXCLUDED.governorate_id,
                geometry = EXCLUDED.geometry
        ''', values)
        
    elif table_name == 'geo_blocks':
        values = [(
            f['properties']['id'],
            f['properties']['name_en'],
            f['properties']['name_ar'],
            f['properties']['district_id'],
            json.dumps(f['geometry'])
        ) for f in data['features']]
        
        execute_values(cur, f'''
            INSERT INTO {table_name} (id, name_en, name_ar, district_id, geometry)
            VALUES %s ON CONFLICT (id) DO UPDATE SET
                name_en = EXCLUDED.name_en,
                name_ar = EXCLUDED.name_ar,
                district_id = EXCLUDED.district_id,
                geometry = EXCLUDED.geometry
        ''', values)
        
    elif table_name == 'geo_police_zones':
        values = [(
            f['properties']['id'],
            f['properties']['name_en'],
            f['properties']['name_ar'],
            f['properties']['governorate_ids'],
            json.dumps(f['geometry'])
        ) for f in data['features']]
        
        execute_values(cur, f'''
            INSERT INTO {table_name} (id, name_en, name_ar, governorate_ids, geometry)
            VALUES %s ON CONFLICT (id) DO UPDATE SET
                name_en = EXCLUDED.name_en,
                name_ar = EXCLUDED.name_ar,
                governorate_ids = EXCLUDED.governorate_ids,
                geometry = EXCLUDED.geometry
        ''', values)
    
    conn.commit()
    print(f"✅ Loaded {len(values)} records into {table_name}")

if __name__ == '__main__':
    conn = psycopg2.connect(**DB_CONFIG)
    
    print("Loading geographic data...")
    load_geojson_to_table('data/geo/kuwait/governorates.geojson', 'geo_governorates', conn)
    load_geojson_to_table('data/geo/kuwait/districts.geojson', 'geo_districts', conn)
    load_geojson_to_table('data/geo/kuwait/blocks.geojson', 'geo_blocks', conn)
    load_geojson_to_table('data/geo/kuwait/police_zones.geojson', 'geo_police_zones', conn)
    
    conn.close()
    print("✅ All geographic data loaded successfully!")
EOF

# 5.2 Run data loading
python load_geo_data.py

# 5.3 Verify data loaded
psql -U bdr.ai -d khareetaty_ai -c "
SELECT 
    'Governorates' as type, COUNT(*) as count FROM geo_governorates
UNION ALL
SELECT 'Districts', COUNT(*) FROM geo_districts
UNION ALL
SELECT 'Blocks', COUNT(*) FROM geo_blocks
UNION ALL
SELECT 'Police Zones', COUNT(*) FROM geo_police_zones;
"

# Expected output:
# type          | count
# --------------+-------
# Governorates  |     6
# Districts     |    30
# Blocks        |    19
# Police Zones  |     6
```

### Step 6: Update Environment Configuration

```bash
# 6.1 Backup current .env
cp .env .env.backup

# 6.2 Add new environment variables
cat >> .env << 'EOF'

# Geographic Enhancement Configuration
GEO_DATA_PATH=data/geo/kuwait/
GEO_FALLBACK_ENABLED=true

# Multiple WhatsApp Contacts (comma-separated)
WHATSAPP_CONTACTS=+96512345678,+96587654321

# Alert Configuration
ALERT_THRESHOLD=10
FORECAST_ALERT_THRESHOLD=15

# Clustering Parameters (per district)
DBSCAN_EPS=0.01
DBSCAN_MIN_SAMPLES=3

# Forecasting
FORECAST_HOURS=24
FORECAST_METHOD=moving_average
EOF

# 6.3 Verify configuration
cat .env | grep -E "GEO_|WHATSAPP_|DBSCAN_|FORECAST_"
```

### Step 7: Test Geographic Resolution

```bash
# 7.1 Test geo lookup service
python -c "
from backend.services.geo_lookup import resolve_zone

# Test Kuwait City coordinates
result = resolve_zone(29.3759, 47.9774)
print(f'✅ Geo Resolution Test: {result}')

assert result.get('governorate') is not None, 'Governorate resolution failed'
assert result.get('district') is not None, 'District resolution failed'
print('✅ All geo resolution tests passed!')
"

# 7.2 Test ETL with geo resolution
python -c "
import sys
sys.path.insert(0, 'automation')
from etl_job import clean_raw_to_clean

# Run ETL (will process any staging files)
clean_raw_to_clean()
print('✅ ETL with geo resolution completed')
"

# 7.3 Verify geo columns populated
psql -U bdr.ai -d khareetaty_ai -c "
SELECT 
    COUNT(*) as total,
    COUNT(district) as with_district,
    COUNT(block) as with_block,
    COUNT(police_zone) as with_police_zone,
    ROUND(COUNT(district) * 100.0 / COUNT(*), 2) as resolution_rate
FROM incidents_clean
WHERE timestamp > NOW() - INTERVAL '7 days';
"

# Expected: resolution_rate should be > 80%
```

### Step 8: Run Analytics Pipeline

```bash
# 8.1 Run clustering (per district)
python services/clustering.py

# 8.2 Verify district-level hotspots
psql -U bdr.ai -d khareetaty_ai -c "
SELECT 
    zone_type,
    district,
    police_zone,
    risk_level,
    incident_count
FROM zones_hotspots
WHERE zone_type = 'district_cluster'
ORDER BY incident_count DESC
LIMIT 10;
"

# 8.3 Run forecasting (per zone)
python services/modeling.py

# 8.4 Verify forecasts
psql -U bdr.ai -d khareetaty_ai -c "
SELECT 
    district,
    police_zone,
    forecast_count,
    forecast_timestamp
FROM zones_hotspots
WHERE forecast_count IS NOT NULL
ORDER BY forecast_count DESC
LIMIT 10;
"
```

### Step 9: Deploy Enhanced Dashboard

```bash
# 9.1 Test dashboard locally
streamlit run src/dashboard_geo_enhanced.py --server.port 8501 &
DASH_PID=$!

# 9.2 Wait for startup
sleep 5

# 9.3 Test dashboard endpoint
curl -I http://localhost:8501

# 9.4 Stop test dashboard
kill $DASH_PID

# 9.5 Configure dashboard service (systemd)
sudo tee /etc/systemd/system/khareetaty-dashboard.service > /dev/null << EOF
[Unit]
Description=Khareetaty-AI Geographic Dashboard
After=network.target postgresql.service

[Service]
Type=simple
User=bdr.ai
WorkingDirectory=/path/to/khareetaty-ai-mvp
Environment="PATH=/path/to/khareetaty-ai-mvp/venv/bin"
ExecStart=/path/to/khareetaty-ai-mvp/venv/bin/streamlit run src/dashboard_geo_enhanced.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 9.6 Enable and start dashboard service
sudo systemctl daemon-reload
sudo systemctl enable khareetaty-dashboard
sudo systemctl start khareetaty-dashboard

# 9.7 Verify dashboard running
sudo systemctl status khareetaty-dashboard
curl -I http://localhost:8501
```

### Step 10: Configure Alerting

```bash
# 10.1 Test alert system
python -c "
from automation.trigger_alerts import trigger_hotspot_alerts

# Dry run (won't send actual messages)
import os
os.environ['DRY_RUN'] = 'true'

trigger_hotspot_alerts()
print('✅ Alert system test completed')
"

# 10.2 Configure alert cron job
crontab -e

# Add line (runs every hour):
# 0 * * * * cd /path/to/khareetaty-ai-mvp && /path/to/venv/bin/python automation/trigger_alerts.py >> /var/log/khareetaty_alerts.log 2>&1

# 10.3 Verify cron job
crontab -l | grep trigger_alerts
```

### Step 11: Restart Services

```bash
# 11.1 Restart API server
sudo systemctl restart khareetaty-api

# 11.2 Restart scheduler
sudo systemctl restart khareetaty-scheduler

# 11.3 Restart dashboard
sudo systemctl restart khareetaty-dashboard

# 11.4 Verify all services running
sudo systemctl status khareetaty-api
sudo systemctl status khareetaty-scheduler
sudo systemctl status khareetaty-dashboard

# 11.5 Check logs
sudo journalctl -u khareetaty-api -n 50 --no-pager
sudo journalctl -u khareetaty-dashboard -n 50 --no-pager
```

### Step 12: Post-Deployment Verification

```bash
# 12.1 Health check
curl http://localhost:8000/health

# 12.2 Test API endpoints
curl http://localhost:8000/api/incidents?limit=5 \
  -H "Authorization: Bearer YOUR_TOKEN"

# 12.3 Test dashboard
curl -I http://localhost:8501

# 12.4 Verify database
psql -U bdr.ai -d khareetaty_ai -c "
SELECT 
    'Incidents with geo' as metric,
    COUNT(*) FILTER (WHERE district IS NOT NULL) as value
FROM incidents_clean
WHERE timestamp > NOW() - INTERVAL '24 hours'
UNION ALL
SELECT 
    'Active hotspots',
    COUNT(*)
FROM zones_hotspots
WHERE zone_type = 'district_cluster'
UNION ALL
SELECT
    'Forecasts generated',
    COUNT(*)
FROM zones_hotspots
WHERE forecast_count IS NOT NULL;
"

# 12.5 Check logs for errors
tail -n 100 /var/log/khareetaty_api.log | grep -i error
tail -n 100 /var/log/khareetaty_alerts.log | grep -i error
```

## 🔄 Rollback Procedure

If issues occur, follow these steps to rollback:

```bash
# 1. Stop services
sudo systemctl stop khareetaty-api
sudo systemctl stop khareetaty-scheduler
sudo systemctl stop khareetaty-dashboard

# 2. Restore database
psql -U bdr.ai -d khareetaty_ai -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
psql -U bdr.ai -d khareetaty_ai < backup_pre_geo_*.sql

# 3. Restore code
cd /path/to/khareetaty-ai-mvp
git checkout main
git reset --hard HEAD~1

# 4. Restore dependencies
pip install -r requirements.txt

# 5. Restart services
sudo systemctl start khareetaty-api
sudo systemctl start khareetaty-scheduler
sudo systemctl start khareetaty-dashboard

# 6. Verify rollback
curl http://localhost:8000/health
```

## 📊 Monitoring & Validation

### Key Metrics to Monitor

```bash
# 1. Geographic resolution rate
psql -U bdr.ai -d khareetaty_ai -c "
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as total_incidents,
    COUNT(district) as resolved,
    ROUND(COUNT(district) * 100.0 / COUNT(*), 2) as resolution_rate
FROM incidents_clean
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
"

# 2. Hotspot detection performance
psql -U bdr.ai -d khareetaty_ai -c "
SELECT 
    zone_type,
    COUNT(*) as hotspot_count,
    AVG(incident_count) as avg_incidents,
    MAX(incident_count) as max_incidents
FROM zones_hotspots
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY zone_type;
"

# 3. Alert delivery status
tail -n 100 /var/log/khareetaty_alerts.log | grep -E "sent|failed"

# 4. Dashboard performance
curl -w "@-" -o /dev/null -s http://localhost:8501 << 'EOF'
time_namelookup:  %{time_namelookup}\n
time_connect:  %{time_connect}\n
time_starttransfer:  %{time_starttransfer}\n
time_total:  %{time_total}\n
EOF
```

### Automated Health Checks

Create monitoring script:

```bash
cat > /usr/local/bin/khareetaty_health_check.sh << 'EOF'
#!/bin/bash

# Health check script for Khareetaty-AI

echo "=== Khareetaty-AI Health Check ==="
echo "Timestamp: $(date)"

# Check API
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$API_STATUS" = "200" ]; then
    echo "✅ API: Healthy"
else
    echo "❌ API: Unhealthy (HTTP $API_STATUS)"
fi

# Check Dashboard
DASH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501)
if [ "$DASH_STATUS" = "200" ]; then
    echo "✅ Dashboard: Healthy"
else
    echo "❌ Dashboard: Unhealthy (HTTP $DASH_STATUS)"
fi

# Check Database
DB_STATUS=$(psql -U bdr.ai -d khareetaty_ai -c "SELECT 1" -t 2>/dev/null)
if [ "$DB_STATUS" = " 1" ]; then
    echo "✅ Database: Healthy"
else
    echo "❌ Database: Unhealthy"
fi

# Check Geo Resolution
GEO_RATE=$(psql -U bdr.ai -d khareetaty_ai -t -c "
SELECT ROUND(COUNT(district) * 100.0 / NULLIF(COUNT(*), 0), 2)
FROM incidents_clean
WHERE timestamp > NOW() - INTERVAL '1 hour'
" 2>/dev/null | xargs)

if [ -n "$GEO_RATE" ] && [ $(echo "$GEO_RATE > 80" | bc) -eq 1 ]; then
    echo "✅ Geo Resolution: ${GEO_RATE}%"
else
    echo "⚠️  Geo Resolution: ${GEO_RATE}% (below threshold)"
fi

echo "==================================="
EOF

chmod +x /usr/local/bin/khareetaty_health_check.sh

# Run health check every 5 minutes
echo "*/5 * * * * /usr/local/bin/khareetaty_health_check.sh >> /var/log/khareetaty_health.log 2>&1" | crontab -
```

## 🔐 Security Considerations

### 1. Secure Environment Variables

```bash
# Ensure .env has restricted permissions
chmod 600 .env

# Verify
ls -l .env
# Should show: -rw------- (600)
```

### 2. Database Access Control

```sql
-- Create read-only user for dashboard
CREATE USER khareetaty_readonly WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE khareetaty_ai TO khareetaty_readonly;
GRANT USAGE ON SCHEMA public TO khareetaty_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO khareetaty_readonly;

-- Update dashboard connection to use read-only user
```

### 3. API Rate Limiting

Ensure rate limiting is configured in backend/app.py:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/incidents")
@limiter.limit("100/minute")
async def get_incidents():
    # ...
```

### 4. WhatsApp Credentials

```bash
# Store credentials securely (use secrets manager in production)
# Never commit .env to git

# Verify .gitignore includes .env
grep "^\.env$" .gitignore || echo ".env" >> .gitignore
```

## 📝 Documentation Updates

After successful deployment:

```bash
# 1. Update README.md
# Add geographic features section

# 2. Update CHANGELOG.md
cat >> CHANGELOG.md << 'EOF'

## [3.0.0] - 2026-01-16

### Added
- Geographic awareness layer with Kuwait administrative boundaries
- District-level hotspot clustering
- Zone-specific 24h forecasting
- Choropleth dashboard with polygon visualization
- Production alert format with full geographic context
- Multi-contact WhatsApp alerting

### Changed
- ETL pipeline now resolves coordinates to zones
- Clustering operates per-district instead of globally
- Forecasting generates predictions per zone
- Database schema includes geo tables and columns

### Dependencies
- Added shapely>=2.0.0
- Added geojson>=3.0.0
- Added rtree>=1.0.0

EOF

# 3. Tag release
git tag -a v3.0.0 -m "Geographic Enhancement Release"
git push origin v3.0.0
```

## 🎯 Success Criteria

Deployment is successful when:

- [ ] All services running (API, Dashboard, Scheduler)
- [ ] Geographic resolution rate > 80%
- [ ] District-level hotspots detected
- [ ] Zone-specific forecasts generated
- [ ] Dashboard displays choropleth maps
- [ ] Alerts include geographic context
- [ ] No errors in logs for 1 hour
- [ ] Health checks passing
- [ ] Performance within acceptable limits (< 5s dashboard load)

## 📞 Support & Troubleshooting

### Common Issues

**Issue: Shapely installation fails**
```bash
# macOS
brew install geos
pip install shapely --no-binary shapely

# Ubuntu
sudo apt-get install libgeos-dev
pip install shapely
```

**Issue: PostGIS not available**
```bash
# Check PostgreSQL version
psql --version

# Install PostGIS
# macOS
brew install postgis

# Ubuntu
sudo apt-get install postgresql-14-postgis-3

# Enable in database
psql -U bdr.ai -d khareetaty_ai -c "CREATE EXTENSION postgis;"
```

**Issue: Dashboard not loading polygons**
```bash
# Check GeoJSON files
ls -lh data/geo/kuwait/

# Verify database has geometry data
psql -U bdr.ai -d khareetaty_ai -c "SELECT COUNT(*) FROM geo_districts WHERE geometry IS NOT NULL;"

# Check Streamlit version
pip install --upgrade streamlit plotly
```

### Contact Information

- **Technical Lead:** bdr.ai
- **Documentation:** [geo_playbook.md](file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/geo_playbook.md)
- **Issue Tracker:** GitHub Issues
- **Emergency Rollback:** See Rollback Procedure above

---

**🚀 Deployment Complete** | **📍 Geographic Intelligence Active** | **✅ Production Ready**
