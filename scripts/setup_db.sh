#!/bin/bash

# Database setup script for XSS Assistant
# This script initializes the PostgreSQL database and runs migrations

set -e  # Exit on error

echo "🔧 XSS Assistant - Database Setup"
echo "=================================="
echo ""

# Load environment variables if .env exists
if [ -f backend/.env ]; then
    echo "📝 Loading configuration from backend/.env..."
    export $(cat backend/.env | grep -v '^#' | xargs)
fi

# Default values
DB_NAME="${DB_NAME:-xss_assistant}"
DB_USER="${DB_USER:-xss_user}"
DB_PASSWORD="${DB_PASSWORD:-change_me}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

echo ""
echo "Database Configuration:"
echo "  Host: $DB_HOST:$DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Check if PostgreSQL is running
echo "🔍 Checking PostgreSQL service..."
if ! pg_isready -h $DB_HOST -p $DB_PORT > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running or not accessible at $DB_HOST:$DB_PORT"
    echo "   Please start PostgreSQL and try again."
    exit 1
fi
echo "✅ PostgreSQL is running"
echo ""

# Create database if it doesn't exist
echo "🗄️  Creating database (if not exists)..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U postgres -c "CREATE DATABASE $DB_NAME"
echo "✅ Database ready"
echo ""

# Create user if it doesn't exist
echo "👤 Creating database user (if not exists)..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U postgres -tc "SELECT 1 FROM pg_user WHERE usename = '$DB_USER'" | grep -q 1 || \
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD'"
echo "✅ User ready"
echo ""

# Grant privileges
echo "🔐 Granting privileges..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER"
echo "✅ Privileges granted"
echo ""

# Run Alembic migrations
echo "🔄 Running database migrations..."
cd backend
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

echo "Running alembic upgrade head..."
alembic upgrade head
echo "✅ Migrations completed"
cd ..
echo ""

echo "🎉 Database setup complete!"
echo ""
echo "Next steps:"
echo "  1. Update backend/.env with your configuration"
echo "  2. Start the backend: uvicorn backend.app.main:app --reload"
echo "  3. Start the worker: python workers/worker.py"
echo ""
echo "API Documentation: http://localhost:8000/docs"
