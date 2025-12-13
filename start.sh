#!/bin/bash

# SOCAR Document Processing - Quick Start Script

set -e

echo "=================================="
echo "SOCAR Document Processing System"
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file with required credentials"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Prerequisites checked"
echo ""

# Create data directories
mkdir -p data/pdfs data/vector_db data/processed
echo "✓ Data directories created"
echo ""

# Build and start containers
echo "🔨 Building Docker image..."
docker-compose build

echo ""
echo "🚀 Starting containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for service to be ready..."
sleep 5

# Wait for health check
MAX_RETRIES=30
RETRY_COUNT=0
until curl -f http://localhost:8000/ &> /dev/null || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
    echo "   Waiting for API... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
    ((RETRY_COUNT++))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo ""
    echo "❌ Failed to start service"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

echo ""
echo "=================================="
echo "✅ SOCAR API is ready!"
echo "=================================="
echo ""
echo "📍 API URL: http://localhost:8000"
echo "📖 Documentation: http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  • View logs:    docker-compose logs -f"
echo "  • Stop:         docker-compose down"
echo "  • Restart:      docker-compose restart"
echo ""
