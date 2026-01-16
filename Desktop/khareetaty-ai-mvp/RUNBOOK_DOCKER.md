# 🐳 KHAREETATY-AI DOCKER COMPOSE RUNBOOK

## Overview

This runbook guides you through deploying the khareetaty-ai platform using Docker Compose. This approach provides:
- **Isolated environments** for each service
- **Easy deployment** with single command
- **Consistent setup** across development, staging, and production
- **Automatic networking** between containers
- **Volume persistence** for database and logs

---

## Prerequisites

### Required Software

1. **Docker Desktop** (includes Docker Compose)
   - macOS: [Download Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
   - Linux: [Install Docker Engine](https://docs.docker.com/engine/install/)
   - Windows: [Download Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

2. **Verify Installation**
```bash
docker --version          # Should be 20.10+
docker-compose --version  # Should be 2.0+
```

### System Requirements
- **RAM**: Minimum 8GB (4GB allocated to Docker)
- **Disk**: 5GB free space
- **CPU**: 2+ cores recommended

---

## 📋 QUICK START

### 1. Clone Repository
```bash
cd ~/Projects
git clone <repository-url>
cd khareetaty-ai-mvp
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit [file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/.env]:
```env
# Database Configuration (Docker internal networking)
DB_HOST=postgres  # Service name from docker-compose.yml
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

**🔑 Important**: Set `DB_HOST=postgres` (not `localhost`) for Docker networking!

### 3. Build and Start Services
```bash
docker-compose up --build -d
```

This command:
- Builds Docker images for all services
- Creates containers
- Starts services in detached mode
- Sets up networking between containers

### 4. Verify Services Are Running
```bash
docker-compose ps
```

Expected output:
```
NAME                    STATUS              PORTS
khareetaty-postgres     Up 30 seconds       0.0.0.0:5432->5432/tcp
khareetaty-api          Up 28 seconds       0.0.0.0:8000->8000/tcp
khareetaty-dashboard    Up 28 seconds       0.0.0.0:8050->8050/tcp
khareetaty-scheduler    Up 28 seconds
```

### 5. Initialize Database
```bash
# Wait 10 seconds for PostgreSQL to be ready
sleep 10

# Run migrations
docker-compose exec api python3 backend/db/migrations.py

# Generate sample data
docker-compose exec api python3 src/sample_data_generator.py
```

### 6. Access Services
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8050
- **Database**: `localhost:5432` (from host machine)

---

## 📜 DOCKER COMPOSE ARCHITECTURE

### Service Overview

The [file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/docker-compose.yml] defines 4 services:

#### 1. **postgres** (Database)
- **Image**: `postgis/postgis:14-3.2`
- **Purpose**: PostgreSQL with PostGIS extension
- **Ports**: `5432:5432`
- **Volumes**: `postgres_data:/var/lib/postgresql/data`
- **Health Check**: Automatic readiness probe

#### 2. **api** (FastAPI Backend)
- **Build**: [file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/Dockerfile]
- **Purpose**: REST API server
- **Ports**: `8000:8000`
- **Depends On**: `postgres`
- **Command**: `uvicorn backend.app:app --host 0.0.0.0 --port 8000`

#### 3. **dashboard** (Dash/Plotly UI)
- **Build**: Same Dockerfile as API
- **Purpose**: Web dashboard
- **Ports**: `8050:8050`
- **Depends On**: `postgres`, `api`
- **Command**: `python3 src/dashboard.py`

#### 4. **scheduler** (Background Jobs)
- **Build**: Same Dockerfile as API
- **Purpose**: Automated pipeline execution
- **Depends On**: `postgres`
- **Command**: `python3 main.py`

### Network Configuration
```yaml
networks:
  khareetaty-network:
    driver: bridge
```

All services communicate via `khareetaty-network`.

### Volume Configuration
```yaml
volumes:
  postgres_data:
    driver: local
```

Database data persists across container restarts.

---

## 🛠️ DOCKER COMMANDS REFERENCE

### Starting Services

```bash
# Start all services (detached)
docker-compose up -d

# Start with build (after code changes)
docker-compose up --build -d

# Start specific service
docker-compose up -d api

# Start with logs visible
docker-compose up
```

### Stopping Services

```bash
# Stop all services (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (DELETES DATA!)
docker-compose down -v

# Stop specific service
docker-compose stop api
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# Follow logs (real-time)
docker-compose logs -f

# View specific service logs
docker-compose logs api
docker-compose logs postgres
docker-compose logs dashboard
docker-compose logs scheduler

# Last 100 lines
docker-compose logs --tail=100

# Logs with timestamps
docker-compose logs -t
```

### Executing Commands in Containers

```bash
# Open bash shell in API container
docker-compose exec api bash

# Run Python script
docker-compose exec api python3 main.py

# Access PostgreSQL
docker-compose exec postgres psql -U bdr.ai -d khareetaty_ai

# Run migrations
docker-compose exec api python3 backend/db/migrations.py

# Generate sample data
docker-compose exec api python3 src/sample_data_generator.py
```

### Inspecting Services

```bash
# List running containers
docker-compose ps

# View service configuration
docker-compose config

# View resource usage
docker stats

# Inspect specific container
docker inspect khareetaty-api
```

### Rebuilding Services

```bash
# Rebuild all images
docker-compose build

# Rebuild specific service
docker-compose build api

# Rebuild without cache (clean build)
docker-compose build --no-cache

# Rebuild and restart
docker-compose up --build -d
```

---

## 📊 MONITORING & HEALTH CHECKS

### Check Service Health

```bash
# API health endpoint
curl http://localhost:8000/health

# Expected response
{"status": "healthy", "timestamp": "2026-01-16T12:00:00"}
```

### Database Health

```bash
# Check PostgreSQL is accepting connections
docker-compose exec postgres pg_isready -U bdr.ai

# Expected output
/var/run/postgresql:5432 - accepting connections
```

### View Container Resource Usage

```bash
docker stats
```

Monitors:
- CPU usage
- Memory usage
- Network I/O
- Block I/O

### Access Container Logs

```bash
# Real-time logs for all services
docker-compose logs -f

# Filter by service
docker-compose logs -f api | grep ERROR
```

---

## 🧪 TESTING THE DEPLOYMENT

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. API Documentation
Open browser: http://localhost:8000/docs

### 3. Register User
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

### 4. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Save the `access_token` from response.

### 5. Get Incidents
```bash
curl http://localhost:8000/api/incidents?limit=10 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. View Dashboard
Open browser: http://localhost:8050

### 7. Trigger Pipeline
```bash
curl -X POST http://localhost:8000/api/pipeline/run \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔧 TROUBLESHOOTING

### Issue: Containers Won't Start

**Check logs**:
```bash
docker-compose logs
```

**Common causes**:
1. Port already in use
   ```bash
   # Find process using port 8000
   lsof -ti:8000
   kill -9 $(lsof -ti:8000)
   ```

2. Insufficient resources
   - Increase Docker Desktop memory allocation
   - Settings → Resources → Memory (set to 4GB+)

3. Build errors
   ```bash
   # Clean rebuild
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Issue: Database Connection Failed

**Verify PostgreSQL is running**:
```bash
docker-compose ps postgres
```

**Check database logs**:
```bash
docker-compose logs postgres
```

**Verify environment variables**:
```bash
docker-compose exec api env | grep DB_
```

**Ensure DB_HOST=postgres** (not localhost)!

**Test connection**:
```bash
docker-compose exec api python3 -c "from src.database import engine; print(engine.connect())"
```

### Issue: API Returns 500 Errors

**Check API logs**:
```bash
docker-compose logs api
```

**Verify migrations ran**:
```bash
docker-compose exec postgres psql -U bdr.ai -d khareetaty_ai -c "\dt"
```

**Re-run migrations**:
```bash
docker-compose exec api python3 backend/db/migrations.py
```

### Issue: Dashboard Not Loading

**Check dashboard logs**:
```bash
docker-compose logs dashboard
```

**Verify dashboard is running**:
```bash
docker-compose ps dashboard
```

**Restart dashboard**:
```bash
docker-compose restart dashboard
```

### Issue: Scheduler Not Running Jobs

**Check scheduler logs**:
```bash
docker-compose logs scheduler
```

**Verify SCHEDULER_ENABLED=true** in `.env`

**Manually trigger pipeline**:
```bash
docker-compose exec scheduler python3 main.py
```

### Issue: Out of Disk Space

**Check Docker disk usage**:
```bash
docker system df
```

**Clean up unused resources**:
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything (CAUTION!)
docker system prune -a --volumes
```

---

## 🔄 DATABASE OPERATIONS

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U bdr.ai khareetaty_ai > backup_$(date +%Y%m%d).sql

# Or using docker cp
docker-compose exec postgres pg_dump -U bdr.ai khareetaty_ai > /tmp/backup.sql
docker cp khareetaty-postgres:/tmp/backup.sql ./backup.sql
```

### Restore Database

```bash
# Copy backup to container
docker cp backup.sql khareetaty-postgres:/tmp/backup.sql

# Restore
docker-compose exec postgres psql -U bdr.ai khareetaty_ai < /tmp/backup.sql
```

### Access PostgreSQL Shell

```bash
docker-compose exec postgres psql -U bdr.ai -d khareetaty_ai
```

```sql
-- List tables
\dt

-- View incidents
SELECT * FROM incidents_clean LIMIT 10;

-- View hotspots
SELECT * FROM zones_hotspots WHERE severity = 'CRITICAL';

-- View alerts
SELECT * FROM alerts_log ORDER BY created_at DESC LIMIT 10;

-- Exit
\q
```

### Reset Database

```bash
# Stop services
docker-compose down

# Remove volume (DELETES ALL DATA!)
docker volume rm khareetaty-ai-mvp_postgres_data

# Restart services
docker-compose up -d

# Re-run migrations
docker-compose exec api python3 backend/db/migrations.py

# Generate sample data
docker-compose exec api python3 src/sample_data_generator.py
```

---

## 🚀 PRODUCTION DEPLOYMENT

### Environment Configuration

Create `.env.production`:
```env
# Use strong passwords!
DB_PASSWORD=<strong-random-password>
JWT_SECRET=<strong-random-secret>

# Production database (external)
DB_HOST=your-production-db.example.com
DB_PORT=5432
DB_NAME=khareetaty_ai_prod

# Real Twilio credentials
TWILIO_ACCOUNT_SID=<real-sid>
TWILIO_AUTH_TOKEN=<real-token>
TWILIO_PHONE_NUMBER=<real-number>

# Disable debug mode
DEBUG=false
```

### Deploy with Production Config

```bash
# Use production environment file
docker-compose --env-file .env.production up -d
```

### Use Docker Swarm (Multi-Node)

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml khareetaty

# List services
docker service ls

# Scale API service
docker service scale khareetaty_api=3
```

### Use Kubernetes (Advanced)

Convert docker-compose to Kubernetes:
```bash
# Install kompose
brew install kompose

# Convert
kompose convert -f docker-compose.yml

# Deploy to Kubernetes
kubectl apply -f .
```

### SSL/TLS with Nginx Reverse Proxy

Add to `docker-compose.yml`:
```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - ./ssl:/etc/nginx/ssl
  depends_on:
    - api
    - dashboard
```

---

## 📊 PERFORMANCE OPTIMIZATION

### Resource Limits

Add to `docker-compose.yml`:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Multi-Stage Builds

Optimize [file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/Dockerfile]:
```dockerfile
# Build stage
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
```

### Connection Pooling

Already configured in [file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/src/database.py]:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

---

## 📚 ADDITIONAL RESOURCES

- **Docker Compose Docs**: https://docs.docker.com/compose/
- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices/
- **PostGIS Docker**: https://registry.hub.docker.com/r/postgis/postgis/
- **FastAPI Docker**: https://fastapi.tiangolo.com/deployment/docker/
- **Project README**: [file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/README.md]
- **Local Runbook**: [file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/RUNBOOK_LOCAL.md]

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] Docker and Docker Compose installed
- [ ] `.env` file configured with correct values
- [ ] `DB_HOST=postgres` (not localhost)
- [ ] Strong passwords set for production
- [ ] Twilio credentials configured
- [ ] Services built successfully
- [ ] All containers running
- [ ] Database migrations applied
- [ ] Sample data generated (dev) or real data loaded (prod)
- [ ] API health check passing
- [ ] Dashboard accessible
- [ ] Authentication working
- [ ] Scheduler running
- [ ] Logs being generated
- [ ] Backups configured

---

**🎉 Your khareetaty-ai platform is now running in Docker!**

For local development without Docker, see [file:///Users/bdr.ai/Desktop/khareetaty-ai-mvp/RUNBOOK_LOCAL.md]