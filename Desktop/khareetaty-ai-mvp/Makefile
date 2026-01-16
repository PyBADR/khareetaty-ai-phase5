# Khareetaty-AI Makefile
# Phase 5 Production Deployment

.PHONY: help build up down restart logs clean db-init seed test health

# Default target
help:
	@echo "Khareetaty-AI - Available Commands:"
	@echo ""
	@echo "  make build        - Build all Docker images"
	@echo "  make up           - Start all services"
	@echo "  make down         - Stop all services"
	@echo "  make restart      - Restart all services"
	@echo "  make logs         - View logs from all services"
	@echo "  make db-init      - Initialize database with migrations"
	@echo "  make seed         - Seed database with sample data"
	@echo "  make test         - Run system tests"
	@echo "  make health       - Check health of all services"
	@echo "  make clean        - Remove all containers and volumes"
	@echo ""

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose -f docker-compose.prod.yml build

# Start all services
up:
	@echo "Starting Khareetaty-AI services..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Services started!"
	@echo "Backend API: http://localhost:8000"
	@echo "Dashboard: http://localhost:8501"
	@echo "API Docs: http://localhost:8000/docs"

# Stop all services
down:
	@echo "Stopping Khareetaty-AI services..."
	docker-compose -f docker-compose.prod.yml down

# Restart all services
restart: down up

# View logs
logs:
	docker-compose -f docker-compose.prod.yml logs -f

# View backend logs only
logs-backend:
	docker-compose -f docker-compose.prod.yml logs -f backend

# View dashboard logs only
logs-dashboard:
	docker-compose -f docker-compose.prod.yml logs -f dashboard

# Initialize database
db-init:
	@echo "Initializing database..."
	docker-compose -f docker-compose.prod.yml exec postgres psql -U bdr.ai -d khareetaty_ai -f /docker-entrypoint-initdb.d/01-phase5-migrations.sql
	docker-compose -f docker-compose.prod.yml exec postgres psql -U bdr.ai -d khareetaty_ai -f /docker-entrypoint-initdb.d/02-migrations.sql
	@echo "Database initialized!"

# Seed database with sample data
seed:
	@echo "Seeding database with sample data..."
	docker-compose -f docker-compose.prod.yml exec backend python generate_sample_data.py
	docker-compose -f docker-compose.prod.yml exec backend python load_geo_data.py
	@echo "Database seeded!"

# Run system tests
test:
	@echo "Running system tests..."
	python test_system.py
	python test_phase5.py
	@echo "Tests completed!"

# Check health of all services
health:
	@echo "Checking service health..."
	@echo ""
	@echo "Backend API:"
	@curl -s http://localhost:8000/health/live | python -m json.tool || echo "Backend not responding"
	@echo ""
	@echo "Database:"
	@curl -s http://localhost:8000/health/ready | python -m json.tool || echo "Database not ready"
	@echo ""
	@echo "Dashboard:"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8501 || echo "Dashboard not responding"

# Clean up everything
clean:
	@echo "Cleaning up all containers and volumes..."
	docker-compose -f docker-compose.prod.yml down -v
	@echo "Cleanup complete!"

# Development mode - run locally without Docker
dev-backend:
	@echo "Starting backend in development mode..."
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-dashboard:
	@echo "Starting dashboard in development mode..."
	streamlit run dashboard_streamlit/app.py --server.port=8501

# Production deployment helpers
deploy-render:
	@echo "Deploying to Render.com..."
	@echo "Make sure you have configured Render.com with your GitHub repository"
	@echo "Backend will be deployed from backend/Dockerfile"

deploy-huggingface:
	@echo "Deploying to Hugging Face Spaces..."
	@echo "Make sure you have configured HF Space with your GitHub repository"
	@echo "Dashboard will be deployed from Dockerfile.streamlit"

# Database backup
db-backup:
	@echo "Backing up database..."
	docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U bdr.ai khareetaty_ai > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup complete!"

# Database restore
db-restore:
	@echo "Restoring database from backup..."
	@read -p "Enter backup file name: " backup_file; \
	docker-compose -f docker-compose.prod.yml exec -T postgres psql -U bdr.ai khareetaty_ai < $$backup_file
	@echo "Restore complete!"
