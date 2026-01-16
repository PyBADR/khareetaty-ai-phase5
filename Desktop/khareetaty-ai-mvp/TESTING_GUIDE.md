# 🧪 Khareetaty AI - Testing Guide

## Complete Testing Procedures for All Phases

---

## 🎯 Phase 1: ETL Pipeline Testing

### Test 1.1: CSV Data Loading
```bash
# Run ETL job
python automation/etl_job.py

# Verify raw data loaded
psql -U bader -d khareetaty_ai << EOF
SELECT COUNT(*) as total_raw FROM incidents_raw;
SELECT incident_type, COUNT(*) FROM incidents_raw GROUP BY incident_type;
EOF

# Expected: 100 rows with various incident types
```

### Test 1.2: Data Cleaning & Transformation
```bash
# Check cleaned data
psql -U bader -d khareetaty_ai << EOF
SELECT COUNT(*) as total_clean FROM incidents_clean;
SELECT hour, COUNT(*) FROM incidents_clean GROUP BY hour ORDER BY hour;
SELECT day, COUNT(*) FROM incidents_clean GROUP BY day;
EOF

# Expected: Same count as raw, with hour/day/week fields populated
```

### Test 1.3: Data Validation
```bash
# Check for invalid coordinates (outside Kuwait)
psql -U bader -d khareetaty_ai << EOF
SELECT COUNT(*) FROM incidents_clean 
WHERE lat < 28.5 OR lat > 30.1 OR lon < 46.5 OR lon > 48.5;
EOF

# Expected: 0 rows (all coordinates should be valid)
```

### Test 1.4: Duplicate Detection
```bash
# Check for duplicates
psql -U bader -d khareetaty_ai << EOF
SELECT lat, lon, timestamp, COUNT(*) 
FROM incidents_clean 
GROUP BY lat, lon, timestamp 
HAVING COUNT(*) > 1;
EOF

# Expected: 0 rows (no duplicates)
```

---

## 🤖 Phase 2: ML & Analytics Testing

### Test 2.1: DBSCAN Clustering
```bash
# Run clustering
python backend/services/clustering.py

# Check hotspots created
psql -U bader -d khareetaty_ai << EOF
SELECT zone, score, predicted FROM zones_hotspots 
WHERE predicted = false 
ORDER BY score DESC;
EOF

# Expected: Multiple clusters with scores
```

### Test 2.2: Prophet Forecasting
```bash
# Run forecasting
python backend/services/modeling.py

# Check predictions
psql -U bader -d khareetaty_ai << EOF
SELECT zone, score, predicted FROM zones_hotspots 
WHERE predicted = true 
ORDER BY created_at DESC 
LIMIT 7;
EOF

# Expected: 7 forecast entries
```

### Test 2.3: Analytics API Endpoint
```bash
# Get JWT token first
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "bader.naser.ai.sa@gmail.com"}' | jq -r '.access_token')

# Run analytics via API
curl -X POST http://localhost:8000/analytics/run \
  -H "Authorization: Bearer $TOKEN"

# Expected: {"status": "analytics refreshed"}
```

### Test 2.4: Hotspot Retrieval
```bash
# Get hotspots
curl http://localhost:8000/analytics/hotspots \
  -H "Authorization: Bearer $TOKEN" | jq

# Expected: JSON array of hotspots with zones and scores
```

### Test 2.5: Forecast Retrieval
```bash
# Get forecast
curl http://localhost:8000/analytics/forecast \
  -H "Authorization: Bearer $TOKEN" | jq

# Expected: JSON array with 7-day predictions
```

---

## 🔐 Phase 3: Authentication Testing

### Test 3.1: User Creation
```bash
# Create test users
psql -U bader -d khareetaty_ai << EOF
INSERT INTO system_users (name, email, phone, role) VALUES
('Test Superadmin', 'superadmin@test.com', '+96511111111', 'superadmin'),
('Test Analyst', 'analyst@test.com', '+96522222222', 'analyst'),
('Test Viewer', 'viewer@test.com', '+96533333333', 'viewer');
EOF

# Verify users created
psql -U bader -d khareetaty_ai -c "SELECT name, email, role FROM system_users;"
```

### Test 3.2: Login & JWT Generation
```bash
# Test login for each role
for email in "superadmin@test.com" "analyst@test.com" "viewer@test.com"; do
  echo "Testing login for: $email"
  curl -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$email\"}" | jq
done

# Expected: Each returns access_token and token_type
```

### Test 3.3: Role-Based Access Control
```bash
# Get tokens for different roles
SUPERADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "superadmin@test.com"}' | jq -r '.access_token')

ANALYST_TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "analyst@test.com"}' | jq -r '.access_token')

VIEWER_TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "viewer@test.com"}' | jq -r '.access_token')

# Test superadmin can run analytics
curl -X POST http://localhost:8000/analytics/run \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN"
# Expected: Success

# Test analyst can run analytics
curl -X POST http://localhost:8000/analytics/run \
  -H "Authorization: Bearer $ANALYST_TOKEN"
# Expected: Success

# Test viewer CANNOT run analytics
curl -X POST http://localhost:8000/analytics/run \
  -H "Authorization: Bearer $VIEWER_TOKEN"
# Expected: 403 Forbidden
```

### Test 3.4: Token Expiration
```bash
# Use an expired or invalid token
curl -X POST http://localhost:8000/analytics/run \
  -H "Authorization: Bearer invalid_token_here"

# Expected: 401 Unauthorized
```

---

## 🎛️ Phase 4: Command & Control Testing

### Test 4.1: Command Dashboard Overview
```bash
curl http://localhost:8000/commands/overview \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" | jq

# Expected: JSON with active_hotspots, predictions, alerts_24h, incidents_today
```

### Test 4.2: Tactical View
```bash
curl http://localhost:8000/commands/tactical \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" | jq

# Expected: JSON with incidents_by_hour, clusters_by_severity, trending_zones
```

### Test 4.3: Manual Alert Sending
```bash
curl -X POST http://localhost:8000/commands/alert \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test alert from API",
    "recipients": ["+96566338736"],
    "priority": "high"
  }' | jq

# Expected: {"status": "alert sent", "recipients": 1}
```

### Test 4.4: Task Assignment
```bash
# Assign a task
curl -X POST http://localhost:8000/tasks/assign \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "zone": "Salmiya Cluster 1",
    "severity": "high",
    "assigned_to": "Team Alpha"
  }' | jq

# Expected: {"task_id": 1, "status": "assigned"}
```

### Test 4.5: View Active Tasks
```bash
curl http://localhost:8000/tasks/active \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" | jq

# Expected: JSON array of active tasks
```

### Test 4.6: Complete Task
```bash
# Complete the task created above
curl -X POST http://localhost:8000/tasks/1/complete \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Patrol completed, area secured"}' | jq

# Expected: {"status": "completed"}
```

### Test 4.7: Escalation Engine
```bash
# Check escalation configuration
cat config/escalation.yaml

# Trigger escalation by creating high-score hotspot
psql -U bader -d khareetaty_ai << EOF
INSERT INTO zones_hotspots (zone, score, predicted)
VALUES ('Test High Risk Zone', 85.0, false);
EOF

# Run alert trigger
python automation/trigger_alerts.py

# Check if alert was sent (check logs or database)
```

### Test 4.8: Audit Logging
```bash
# Check audit log
psql -U bader -d khareetaty_ai << EOF
SELECT user_email, action, timestamp 
FROM action_log 
ORDER BY timestamp DESC 
LIMIT 10;
EOF

# Expected: Recent actions logged
```

---

## 🌐 Phase 5: National Grid Testing

### Test 5.1: Service Account Creation
```bash
# Create service account
curl -X POST http://localhost:8000/interop/service-accounts \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MOI Test Feed",
    "permissions": ["ingest:incidents", "ingest:moi"]
  }' | jq

# Save the API key from response
API_KEY="<api_key_from_response>"
```

### Test 5.2: Multi-Agency Data Ingestion
```bash
# Test MOI ingestion
curl -X POST http://localhost:8000/interop/ingest/moi \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_type": "theft",
    "governorate": "Hawally",
    "zone": "Salmiya",
    "lat": 29.3375,
    "lon": 48.0758,
    "timestamp": "2026-01-16T14:30:00",
    "severity": "medium"
  }' | jq

# Expected: {"status": "ingested", "stream": "moi"}

# Test Fire/EMS ingestion
curl -X POST http://localhost:8000/interop/ingest/fire \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_type": "fire",
    "lat": 29.3759,
    "lon": 47.9774,
    "timestamp": "2026-01-16T14:35:00",
    "units_dispatched": 3
  }' | jq

# Test Traffic ingestion
curl -X POST http://localhost:8000/interop/ingest/traffic \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_type": "accident",
    "lat": 29.3000,
    "lon": 48.0000,
    "timestamp": "2026-01-16T14:40:00",
    "severity": "major"
  }' | jq
```

### Test 5.3: IoT Sensor Data Processing
```bash
# Send camera motion event
curl -X POST http://localhost:8000/interop/ingest/iot \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_type": "camera",
    "sensor_id": "CAM_001",
    "event_type": "motion_detected",
    "lat": 29.3375,
    "lon": 48.0758,
    "timestamp": "2026-01-16T14:45:00",
    "metadata": {"confidence": 0.95}
  }' | jq

# Send crowd density alert
curl -X POST http://localhost:8000/interop/ingest/iot \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_type": "camera",
    "sensor_id": "CAM_002",
    "event_type": "crowd_density",
    "lat": 29.3400,
    "lon": 48.0800,
    "timestamp": "2026-01-16T14:50:00",
    "metadata": {"density": 85, "threshold": 70}
  }' | jq
```

### Test 5.4: IoT Analytics
```bash
# Get IoT risk scores
curl http://localhost:8000/iot/risk-scores \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" | jq

# Get camera status
curl http://localhost:8000/iot/camera-status \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" | jq

# Get anomalies
curl http://localhost:8000/iot/anomalies \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" | jq
```

### Test 5.5: Predictive Patrol Allocation
```bash
# Get tomorrow's predictions
curl http://localhost:8000/patrol/predict-tomorrow \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" | jq

# Get patrol recommendations
curl http://localhost:8000/patrol/recommend-routes \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" | jq

# Auto-assign patrols
curl -X POST http://localhost:8000/patrol/auto-assign \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" | jq

# Check coverage gaps
curl http://localhost:8000/patrol/coverage-gaps \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" | jq
```

### Test 5.6: Data Broker Streams
```bash
# Check stream statistics
curl http://localhost:8000/data-broker/stats \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" | jq

# Monitor streams
curl http://localhost:8000/data-broker/monitor \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" | jq

# Expected: Stream info for moi, fire, traffic, iot, etc.
```

### Test 5.7: Webhook Integration
```bash
# Register webhook
curl -X POST http://localhost:8000/interop/webhooks \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://external-system.example.com/webhook",
    "events": ["hotspot_detected", "alert_triggered"],
    "secret": "webhook_secret_key"
  }' | jq

# Test webhook delivery
curl -X POST http://localhost:8000/interop/webhooks/test \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"webhook_id": 1}' | jq
```

### Test 5.8: Rate Limiting
```bash
# Send 150 requests rapidly (should hit 100/min limit)
for i in {1..150}; do
  curl -X POST http://localhost:8000/interop/ingest/moi \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "incident_type": "test",
      "lat": 29.3,
      "lon": 48.0,
      "timestamp": "2026-01-16T15:00:00"
    }' &
done
wait

# Expected: Some requests return 429 Too Many Requests
```

---

## 🏥 Health & Monitoring Testing

### Test 6.1: Health Check
```bash
curl http://localhost:8000/health | jq

# Expected: {"status": "healthy", "database": "connected", "redis": "connected"}
```

### Test 6.2: Database Connection Pool
```bash
# Check active connections
psql -U bader -d khareetaty_ai << EOF
SELECT count(*) as active_connections 
FROM pg_stat_activity 
WHERE datname = 'khareetaty_ai';
EOF
```

### Test 6.3: Redis Connection (if using Phase 5)
```bash
redis-cli ping
# Expected: PONG

redis-cli INFO | grep connected_clients
# Expected: connected_clients:N
```

---

## 🚀 Performance Testing

### Test 7.1: API Response Time
```bash
# Test analytics endpoint response time
time curl -X POST http://localhost:8000/analytics/run \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN"

# Expected: < 2 seconds for small dataset
```

### Test 7.2: Concurrent Requests
```bash
# Use Apache Bench
ab -n 1000 -c 10 -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  http://localhost:8000/analytics/hotspots

# Expected: All requests succeed, avg response time < 500ms
```

### Test 7.3: Database Query Performance
```bash
# Explain query plan for hotspot retrieval
psql -U bader -d khareetaty_ai << EOF
EXPLAIN ANALYZE 
SELECT zone, score FROM zones_hotspots 
WHERE predicted = false 
ORDER BY score DESC 
LIMIT 10;
EOF

# Check for index usage and execution time
```

---

## 🔄 Integration Testing

### Test 8.1: End-to-End Pipeline
```bash
# 1. Ingest new data
curl -X POST http://localhost:8000/interop/ingest/moi \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_type": "theft",
    "lat": 29.3375,
    "lon": 48.0758,
    "timestamp": "2026-01-16T16:00:00"
  }'

# 2. Run analytics
curl -X POST http://localhost:8000/analytics/run \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN"

# 3. Check if new hotspot detected
curl http://localhost:8000/analytics/hotspots \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" | jq

# 4. Verify alert triggered (if threshold exceeded)
psql -U bader -d khareetaty_ai -c "SELECT * FROM alerts_log ORDER BY created_at DESC LIMIT 1;"
```

### Test 8.2: Automated Daily Job
```bash
# Manually trigger the scheduled job
python -c "
from backend.app import daily_jobs
daily_jobs()
"

# Check logs for execution
tail -f backend/logs/scheduler.log
```

---

## 📊 Data Quality Testing

### Test 9.1: Data Completeness
```bash
psql -U bader -d khareetaty_ai << EOF
-- Check for NULL values in critical fields
SELECT 
  COUNT(*) FILTER (WHERE incident_type IS NULL) as null_type,
  COUNT(*) FILTER (WHERE lat IS NULL) as null_lat,
  COUNT(*) FILTER (WHERE lon IS NULL) as null_lon,
  COUNT(*) FILTER (WHERE timestamp IS NULL) as null_timestamp
FROM incidents_clean;
EOF

# Expected: All zeros
```

### Test 9.2: Data Consistency
```bash
psql -U bader -d khareetaty_ai << EOF
-- Check if raw and clean counts match
SELECT 
  (SELECT COUNT(*) FROM incidents_raw) as raw_count,
  (SELECT COUNT(*) FROM incidents_clean) as clean_count;
EOF

# Expected: Counts should match
```

---

## ✅ Test Summary Checklist

### Phase 1: ETL
- [ ] CSV loads successfully
- [ ] Data cleaning works
- [ ] Validation catches errors
- [ ] No duplicates created

### Phase 2: ML & Analytics
- [ ] Clustering detects hotspots
- [ ] Forecasting generates predictions
- [ ] Analytics API works
- [ ] Results are reasonable

### Phase 3: Authentication
- [ ] Users can login
- [ ] JWT tokens generated
- [ ] RBAC enforced correctly
- [ ] Invalid tokens rejected

### Phase 4: Command & Control
- [ ] Dashboard shows data
- [ ] Alerts can be sent
- [ ] Tasks can be assigned
- [ ] Audit log captures actions

### Phase 5: National Grid
- [ ] Multi-agency ingestion works
- [ ] IoT data processed
- [ ] Patrol allocation functional
- [ ] Webhooks deliver
- [ ] Rate limiting enforced

### System Health
- [ ] Health check passes
- [ ] Database connected
- [ ] Redis connected (if used)
- [ ] No errors in logs

### Performance
- [ ] API responds quickly
- [ ] Handles concurrent requests
- [ ] Database queries optimized

---

## 🐛 Debugging Tips

### View Backend Logs
```bash
tail -f backend/logs/app.log
```

### Check Database Logs
```bash
# macOS
tail -f /usr/local/var/log/postgresql@14.log

# Linux
tail -f /var/log/postgresql/postgresql-14-main.log
```

### Test Database Connection
```bash
psql -U bader -d khareetaty_ai -c "SELECT version();"
```

### Clear Redis Cache
```bash
redis-cli FLUSHALL
```

### Reset Database
```bash
psql -U bader -d khareetaty_ai << EOF
TRUNCATE incidents_raw, incidents_clean, zones_hotspots, alerts_log, action_log CASCADE;
EOF
```

---

**🎉 All tests passing? Your Khareetaty AI platform is production-ready!**
