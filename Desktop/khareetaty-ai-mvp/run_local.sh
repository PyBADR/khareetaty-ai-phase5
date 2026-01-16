#!/bin/bash
# Khareetaty AI - Local Development Runbook

set -e

echo "🚀 Khareetaty AI - Starting Local Development Environment"

# Check if required tools are installed
echo "🔍 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ is required"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is required"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/staging data/archive logs

# Generate sample data if staging directory is empty
if [ -z "$(ls -A data/staging 2>/dev/null)" ]; then
    echo "📊 Generating sample data..."
    python3 generate_sample_data.py
fi

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are healthy
echo "🏥 Checking service health..."

# Check PostgreSQL
if docker-compose exec postgres pg_isready -U bader -d khareetaty_ai &>/dev/null; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
    exit 1
fi

# Check Redis
if docker-compose exec redis redis-cli ping &>/dev/null; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis is not ready"
    exit 1
fi

# Run database migrations
echo "📋 Running database migrations..."
docker-compose exec postgres psql -U bader -d khareetaty_ai -f /docker-entrypoint-initdb.d/01-migrations.sql

# Start backend service
echo "🚀 Starting backend service..."
docker-compose up -d backend

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 15

# Test backend health
if curl -f http://localhost:8000/health &>/dev/null; then
    echo "✅ Backend is ready"
else
    echo "❌ Backend is not responding"
    docker-compose logs backend
    exit 1
fi

# Start dashboard (optional)
echo ""
echo "📊 Dashboard will be available at: http://localhost:8501"
echo "💻 API documentation: http://localhost:8000/docs"
echo "🏥 Health check: http://localhost:8000/health"
echo ""
echo "🔧 To stop services: docker-compose down"
echo "📋 To view logs: docker-compose logs -f"
echo "🔄 To restart: ./run_local.sh"

# Keep script running to show logs
echo ""
echo "📋 Showing backend logs (Ctrl+C to stop)..."
docker-compose logs -f backend