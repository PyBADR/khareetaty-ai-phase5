ls -la data/
#!/bin/bash

# Khareetaty AI - Database Setup Script
# This script initializes the PostgreSQL database with PostGIS and runs migrations

set -e  # Exit on error

echo "🚀 Khareetaty AI - Database Setup"
echo "================================="

# Configuration
DB_NAME="khareetaty_ai"
DB_USER="bdr.ai"
DB_PASSWORD="secret123"
DB_HOST="localhost"
DB_PORT="5432"

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install it first:"
    echo "   macOS: brew install postgresql"
    echo "   Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

echo "✅ PostgreSQL found"

# Check if PostgreSQL is running
if ! pg_isready -h $DB_HOST -p $DB_PORT &> /dev/null; then
    echo "⚠️  PostgreSQL is not running. Starting it..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start postgresql
    else
        sudo service postgresql start
    fi
    sleep 2
fi

echo "✅ PostgreSQL is running"

# Create database if it doesn't exist
echo "📦 Creating database '$DB_NAME'..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"

echo "✅ Database '$DB_NAME' ready"

# Enable PostGIS extension
echo "🗺️  Enabling PostGIS extension..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS postgis;"

echo "✅ PostGIS enabled"

# Run migrations
echo "📋 Running database migrations..."
if [ -f "backend/db/migrations.sql" ]; then
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f backend/db/migrations.sql
    echo "✅ Migrations completed"
else
    echo "❌ Migration file not found: backend/db/migrations.sql"
    exit 1
fi

# Verify tables
echo "🔍 Verifying tables..."
TABLES=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
echo "✅ Found $TABLES tables"

# Show created tables
echo ""
echo "📊 Database Tables:"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\dt"

# Show system users
echo ""
echo "👥 System Users:"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT id, name, email, role, active FROM system_users;"

echo ""
echo "✅ Database setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure your settings"
echo "2. Run ETL: python automation/etl_job.py"
echo "3. Start API: cd backend && uvicorn app:app --reload"
echo ""
