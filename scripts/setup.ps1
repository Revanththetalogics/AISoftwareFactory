#
# AI Software Factory - Setup Script for Windows PowerShell
#
# This script sets up the development environment for the AI Software Factory
# backend on Windows systems.
#
# Usage:
#   .\scripts\setup.ps1

param(
    [switch]$SkipTests,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "AI Software Factory - Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check Python version
Write-Status "Checking Python version..."
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python (\d+)\.(\d+)") {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
        Write-Error "Python 3.11 or higher is required (found $major.$minor)"
        exit 1
    }
    Write-Status "Python version: $major.$minor"
} else {
    Write-Error "Could not determine Python version"
    exit 1
}

# Check if pip is installed
Write-Status "Checking pip..."
$pipVersion = pip --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "pip is not installed"
    exit 1
}
Write-Status "pip is available"

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Status "Creating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
Write-Status "Activating virtual environment..."
$venvScripts = Join-Path "venv" "Scripts"
$activateScript = Join-Path $venvScripts "Activate.ps1"

if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Error "Could not find virtual environment activation script"
    exit 1
}

# Upgrade pip
Write-Status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
Write-Status "Installing Python dependencies..."
pip install -r backend\requirements.txt

# Create .env file if it doesn't exist
if (-not (Test-Path "backend\.env")) {
    Write-Status "Creating .env file from template..."
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Warning "Please update backend\.env with your configuration"
}

# Create necessary directories
Write-Status "Creating necessary directories..."
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "data" | Out-Null

# Run tests to verify setup (unless skipped)
if (-not $SkipTests) {
    Write-Status "Running tests to verify setup..."
    Push-Location backend
    python -m pytest tests\ -v --tb=short
    Pop-Location
}

Write-Status "Setup complete!"
Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "1. Update backend\.env with your configuration"
Write-Host "2. Start the server:"
Write-Host "   cd backend"
Write-Host "   ..\venv\Scripts\activate"
Write-Host "   uvicorn main:app --reload --port 8000"
Write-Host ""
Write-Host "3. Test the health endpoint:"
Write-Host "   Invoke-RestMethod -Uri http://localhost:8000/api/v1/health"
Write-Host ""
Write-Host "4. View API documentation:"
Write-Host "   http://localhost:8000/docs"
Write-Host "==================================" -ForegroundColor Cyan
