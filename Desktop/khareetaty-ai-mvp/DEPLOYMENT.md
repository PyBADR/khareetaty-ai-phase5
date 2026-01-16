# Khareetaty AI - High Availability Deployment Guide

## Overview

This guide covers deploying Khareetaty AI in a high-availability configuration with:
- Load-balanced backend instances (3+ replicas)
- PostgreSQL primary-replica setup
- Redis primary-replica setup
- Nginx load balancer
- Prometheus + Grafana monitoring
- Elasticsearch + Kibana logging
- Automated health checks
- Auto-scaling capabilities

---

## Architecture

```
                    ┌─────────────────┐
                    │  Nginx Load      │
                    │  Balancer        │
                    └───────┬─────────┘
                            │
         ┌──────────┼──────────┐
         │              │              │
    ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
    │ Backend  │   │ Backend  │   │ Backend  │
    │    1     │   │    2     │   │    3     │
    └────┬────┘   └────┬────┘   └────┬────┘
         │              │              │
         └──────────┬──────────┘
                        │
         ┌─────────────┴─────────────┐
         │                                │
    ┌────┴────┐                  ┌────┴────┐
    │ Postgres │                  │  Redis   │
    │ Primary  │                  │ Primary  │
    └────┬────┘                  └────┬────┘
         │                              │
    ┌────┴────┐                  ┌────┴────┐
    │ Postgres │                  │  Redis   │
    │ Replica  │                  │ Replica  │
    └─────────┘                  └─────────┘
```

---

## Deployment Options

### Option 1: Docker Compose (Development/Small Scale)

**Prerequisites:**
- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 50GB disk space

**Steps:**

```bash
# 1. Clone repository
git clone https://github.com/your-org/khareetaty-ai-mvp.git
cd khareetaty-ai-mvp

# 2. Create environment file
cp .env.example .env
# Edit .env with your configuration

# 3. Deploy with high availability
docker-compose -f docker-compose.ha.yml up -d

# 4. Check status
docker-compose -f docker-compose.ha.yml ps

# 5. View logs
docker-compose -f docker-compose.ha.yml logs -f

# 6. Access services
# API: http://localhost:80
# Grafana: http://localhost:3000 (admin/admin123)
# Prometheus: http://localhost:9090
# Kibana: http://localhost:5601
```

**Scaling:**
```bash
# Scale backend instances
docker-compose -f docker-compose.ha.yml up -d --scale backend=5
```

---

### Option 2: Kubernetes (Production)

**Prerequisites:**
- Kubernetes cluster 1.24+
- kubectl configured
- Helm 3.0+
- 16GB RAM minimum per node
- 100GB disk space

**Steps:**

```bash
# 1. Create namespace
kubectl apply -f kubernetes/deployment.yaml

# 2. Verify deployment
kubectl get pods -n khareetaty
kubectl get services -n khareetaty

# 3. Check pod status
kubectl describe pod <pod-name> -n khareetaty

# 4. View logs
kubectl logs -f <pod-name> -n khareetaty

# 5. Access services
kubectl port-forward svc/khareetaty-backend-service 8000:8000 -n khareetaty
```

**Auto-scaling:**
```bash
# HPA is configured automatically
# View HPA status
kubectl get hpa -n khareetaty

# Manual scaling
kubectl scale deployment khareetaty-backend --replicas=5 -n khareetaty
```

---

## Monitoring Setup

### Prometheus

**Access:** http://localhost:9090

**Key Metrics:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `postgres_up` - PostgreSQL health
- `redis_up` - Redis health

### Grafana

**Access:** http://localhost:3000
**Default credentials:** admin / admin123

**Dashboards:**
1. System Overview
2. API Performance
3. Database Metrics
4. Redis Metrics
5. Error Rates

### Elasticsearch + Kibana

**Kibana Access:** http://localhost:5601

**Log aggregation:**
- All backend logs
- Nginx access logs
- Database logs
- Error tracking

---

## Health Checks

### Automated Health Monitoring

The health check service continuously monitors:
- All backend instances
- PostgreSQL primary and replica
- Redis primary and replica
- Nginx load balancer

**Configure alerts:**
```bash
# Set webhook URL for alerts
export ALERT_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Restart health check service
docker-compose -f docker-compose.ha.yml restart healthcheck
```

### Manual Health Checks

```bash
# Check backend health
curl http://localhost/health

# Check specific backend instance
curl http://localhost:8000/health

# Check database
psql -h localhost -U bader -d khareetaty_ai -c "SELECT 1;"

# Check Redis
redis-cli -h localhost ping
```

---

## Backup & Recovery

### Database Backup

```bash
# Automated daily backup
docker exec khareetaty-postgres-primary pg_dump -U bader khareetaty_ai > backup_$(date +%Y%m%d).sql

# Restore from backup
docker exec -i khareetaty-postgres-primary psql -U bader khareetaty_ai < backup_20260116.sql
```

### Redis Backup

```bash
# Trigger save
docker exec khareetaty-redis-primary redis-cli BGSAVE

# Copy RDB file
docker cp khareetaty-redis-primary:/data/dump.rdb ./redis_backup.rdb
```

---

## Failover Procedures

### Backend Instance Failure

**Automatic:** Nginx automatically routes traffic to healthy instances

**Manual recovery:**
```bash
# Restart failed instance
docker-compose -f docker-compose.ha.yml restart backend-1

# Or in Kubernetes
kubectl delete pod <failed-pod> -n khareetaty
```

### Database Failover

**Promote replica to primary:**
```bash
# 1. Stop primary
docker-compose -f docker-compose.ha.yml stop postgres-primary

# 2. Promote replica
docker exec khareetaty-postgres-replica pg_ctl promote

# 3. Update backend configuration
# Change DATABASE_HOST to postgres-replica

# 4. Restart backends
docker-compose -f docker-compose.ha.yml restart backend-1 backend-2 backend-3
```

### Redis Failover

**Promote replica to primary:**
```bash
# 1. Stop primary
docker-compose -f docker-compose.ha.yml stop redis-primary

# 2. Promote replica
docker exec khareetaty-redis-replica redis-cli REPLICAOF NO ONE

# 3. Update backend configuration
# Change REDIS_HOST to redis-replica
```

---

## Performance Tuning

### Backend Optimization

```python
# In app.py, adjust worker count
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        workers=4,  # Adjust based on CPU cores
        log_level="info"
    )
```

### Database Optimization

```sql
-- Increase connection pool
ALTER SYSTEM SET max_connections = 200;

-- Optimize memory
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';

-- Reload configuration
SELECT pg_reload_conf();
```

### Redis Optimization

```bash
# Increase max memory
docker exec khareetaty-redis-primary redis-cli CONFIG SET maxmemory 1gb

# Set eviction policy
docker exec khareetaty-redis-primary redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

---

## Security Hardening

### SSL/TLS Configuration

1. **Generate certificates:**
```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

2. **Update nginx.conf** (uncomment SSL server block)

3. **Restart Nginx:**
```bash
docker-compose -f docker-compose.ha.yml restart nginx
```

### Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### API Rate Limiting

Configured in `nginx.conf`:
- Authentication endpoints: 10 requests/minute
- API endpoints: 100 requests/minute

---

## Troubleshooting

### Common Issues

**1. Backend not starting:**
```bash
# Check logs
docker-compose -f docker-compose.ha.yml logs backend-1

# Check database connection
docker exec khareetaty-backend-1 python -c "import psycopg2; psycopg2.connect(host='postgres-primary', dbname='khareetaty_ai', user='bader', password='secret123')"
```

**2. High memory usage:**
```bash
# Check container stats
docker stats

# Restart services
docker-compose -f docker-compose.ha.yml restart
```

**3. Database connection errors:**
```bash
# Check PostgreSQL logs
docker logs khareetaty-postgres-primary

# Verify connection
psql -h localhost -U bader -d khareetaty_ai
```

---

## Maintenance

### Updates

```bash
# Pull latest images
docker-compose -f docker-compose.ha.yml pull

# Restart with zero downtime
docker-compose -f docker-compose.ha.yml up -d --no-deps --build backend-1
docker-compose -f docker-compose.ha.yml up -d --no-deps --build backend-2
docker-compose -f docker-compose.ha.yml up -d --no-deps --build backend-3
```

### Database Maintenance

```bash
# Vacuum database
docker exec khareetaty-postgres-primary psql -U bader -d khareetaty_ai -c "VACUUM ANALYZE;"

# Reindex
docker exec khareetaty-postgres-primary psql -U bader -d khareetaty_ai -c "REINDEX DATABASE khareetaty_ai;"
```

---

## Support

For issues or questions:
- Email: bader.naser.ai.sa@gmail.com
- Documentation: https://docs.khareetaty.gov.kw
- GitHub Issues: https://github.com/your-org/khareetaty-ai-mvp/issues
