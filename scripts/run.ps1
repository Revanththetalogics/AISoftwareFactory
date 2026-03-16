#
# AI Software Factory - Run Script for Windows PowerShell
#
# This script runs the AI Software Factory backend server.
#
# Usage:
#   .\scripts\run.ps1 [development|production]

param(
    [string]$Environment = "development"
)

$ErrorActionPreference = "Stop"

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "AI Software Factory - Server" -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Error "Virtual environment not found. Please run setup.ps1 first."
    exit 1
}

# Activate virtual environment
$activateScript = Join-Path "venv" "Scripts" "Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Error "Could not find virtual environment activation script"
    exit 1
}

# Set environment variable
$env:ENVIRONMENT = $Environment

# Change to backend directory and run server
Push-Location backend

try {
    if ($Environment -eq "production") {
        Write-Host "Starting production server..." -ForegroundColor Green
        uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
    } else {
        Write-Host "Starting development server..." -ForegroundColor Green
        uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    }
} finally {
    Pop-Location
}
