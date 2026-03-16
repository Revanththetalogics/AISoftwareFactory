#!/bin/bash
#
# AI Software Factory - Setup Script for WSL/Linux
#
# This script sets up the development environment for the AI Software Factory
# backend on WSL or Linux systems.
#
# Usage:
#   chmod +x scripts/setup.sh
#   ./scripts/setup.sh

set -e  # Exit on error

echo "=================================="
echo "AI Software Factory - Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in WSL
if grep -q Microsoft /proc/version; then
    print_status "Detected WSL environment"
fi

# Check Python version
print_status "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)"
    exit 1
fi
print_status "Python version: $PYTHON_VERSION"

# Check if pip is installed
print_status "Checking pip..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed"
    exit 1
fi
print_status "pip is available"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing Python dependencies..."
pip install -r backend/requirements.txt

# Create .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    print_status "Creating .env file from template..."
    cp backend/.env.example backend/.env
    print_warning "Please update backend/.env with your configuration"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p data

# Run tests to verify setup
print_status "Running tests to verify setup..."
cd backend
python -m pytest tests/ -v --tb=short

print_status "Setup complete!"
echo ""
echo "=================================="
echo "Next Steps:"
echo "=================================="
echo "1. Update backend/.env with your configuration"
echo "2. Start the server:"
echo "   cd backend"
echo "   source ../venv/bin/activate"
echo "   uvicorn main:app --reload --port 8000"
echo ""
echo "3. Test the health endpoint:"
echo "   curl http://localhost:8000/api/v1/health"
echo ""
echo "4. View API documentation:"
echo "   http://localhost:8000/docs"
echo "=================================="
