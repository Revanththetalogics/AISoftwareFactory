#!/bin/bash
#
# AI Software Factory - Run Script for WSL/Linux
#
# This script runs the AI Software Factory backend server.
#
# Usage:
#   chmod +x scripts/run.sh
#   ./scripts/run.sh [development|production]

set -e

ENVIRONMENT=${1:-development}

echo "=================================="
echo "AI Software Factory - Server"
echo "Environment: $ENVIRONMENT"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Change to backend directory
cd backend

# Set environment variables
export ENVIRONMENT=$ENVIRONMENT

if [ "$ENVIRONMENT" == "production" ]; then
    echo "Starting production server..."
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
else
    echo "Starting development server..."
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi
