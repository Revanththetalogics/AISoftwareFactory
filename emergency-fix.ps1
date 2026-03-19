# Emergency Backend Fix Script for Windows
# Fixes uvicorn missing dependency issue

Write-Host "🔧 Emergency Backend Container Fix" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Stop the crashing backend container
Write-Host "🛑 Stopping backend container..." -ForegroundColor Yellow
docker stop ai-factory-backend 2>$null
if ($LASTEXITCODE -eq 0) { Write-Host "Stopped successfully" -ForegroundColor Green } else { Write-Host "Container not running" -ForegroundColor Gray }

# Remove the container
Write-Host "🗑️ Removing container..." -ForegroundColor Yellow
docker rm ai-factory-backend 2>$null
if ($LASTEXITCODE -eq 0) { Write-Host "Removed successfully" -ForegroundColor Green } else { Write-Host "Container not present" -ForegroundColor Gray }

# Pull the latest image
Write-Host "📥 Pulling latest backend image..." -ForegroundColor Yellow
docker pull revanth2245/aisoftwarefactory-backend:staging

# Create a temporary fix by installing uvicorn manually
Write-Host "🛠️ Creating fixed container with uvicorn..." -ForegroundColor Yellow

# Get current directory for volume mounting
$currentDir = Get-Location

# Run container with manual uvicorn installation
docker run -d `
  --name ai-factory-backend-temp `
  --restart unless-stopped `
  -p 8000:8000 `
  -e ENVIRONMENT=production `
  -e LOG_LEVEL=info `
  -e DATABASE_URL="postgresql://aifactory:${env:POSTGRES_PASSWORD}@postgres:5432/aifactory" `
  -e REDIS_URL=redis://redis:6379 `
  -e OLLAMA_URL=http://ollama:11434 `
  -e SECRET_KEY=$env:SECRET_KEY `
  -e ENABLE_METRICS=true `
  -e METRICS_PORT=9090 `
  -v "backend_data:/app/data" `
  -v "${currentDir}\logs\backend:/app/logs" `
  --network ai-factory-network `
  revanth2245/aisoftwarefactory-backend:staging `
  sh -c "pip install uvicorn && python main.py"

Write-Host "⏱️ Waiting for container to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check if container is running
$containerRunning = docker ps | Select-String "ai-factory-backend-temp"
if ($containerRunning) {
    Write-Host "✅ Temporary fix applied successfully!" -ForegroundColor Green
    Write-Host "📦 Container is now running with uvicorn installed" -ForegroundColor White
    
    # Rename container to original name
    Write-Host "🔄 Renaming container..." -ForegroundColor Yellow
    docker rename ai-factory-backend-temp ai-factory-backend
    
    Write-Host "📋 Checking container status..." -ForegroundColor Yellow
    docker ps | Select-String "ai-factory-backend"
    
    Write-Host "🧪 Testing backend access..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10 -ErrorAction Stop
        Write-Host "🎉 Backend is now accessible!" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Backend started but health check failed" -ForegroundColor Yellow
        Write-Host "📋 Check logs: docker logs ai-factory-backend" -ForegroundColor White
    }
} else {
    Write-Host "❌ Fix failed - checking logs..." -ForegroundColor Red
    docker logs ai-factory-backend-temp 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Host "No logs available" -ForegroundColor Gray }
}

Write-Host ""
Write-Host "💡 Next steps:" -ForegroundColor Cyan
Write-Host "1. Update your backend Docker image to include uvicorn permanently" -ForegroundColor White
Write-Host "2. Rebuild and redeploy with proper dependencies" -ForegroundColor White
Write-Host "3. Consider using an official FastAPI/Uvicorn base image" -ForegroundColor White