#!/bin/bash

# NeuroGenesis Docker Run Script
# This script builds and runs the project using Docker

set -e

echo "🐳 NeuroGenesis Docker Setup"
echo "=============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

echo "✓ Docker and docker-compose found"
echo ""

# Build and run
echo "🔨 Building Docker image..."
docker-compose build

echo ""
echo "🚀 Starting NeuroGenesis container..."
docker-compose up -d

echo ""
echo "✅ NeuroGenesis is running!"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop:"
echo "  docker-compose down"
echo ""
echo "To enter the container:"
echo "  docker-compose exec neurogenesis bash"
