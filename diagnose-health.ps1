# Windows Container Health Diagnostic Script

Write-Host "🏥 Container Health Diagnostic" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

Write-Host "📋 Checking container statuses..." -ForegroundColor Yellow
docker-compose -f docker-compose.portainer.yml ps

Write-Host ""
Write-Host "🔍 Checking unhealthy containers..." -ForegroundColor Yellow
$unhealthyContainers = docker-compose -f docker-compose.portainer.yml ps | Select-String "unhealthy" | ForEach-Object { ($_ -split '\s+')[0] }

if ($unhealthyContainers.Count -eq 0) {
    Write-Host "✅ All containers are healthy!" -ForegroundColor Green
    exit 0
}

Write-Host "⚠️  Unhealthy containers found:" -ForegroundColor Red
$unhealthyContainers | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }

Write-Host ""
Write-Host "📝 Getting detailed logs for unhealthy containers..." -ForegroundColor Yellow

foreach ($container in $unhealthyContainers) {
    Write-Host ""
    Write-Host "--- Logs for $container ---" -ForegroundColor Cyan
    docker logs --tail 50 $container
    
    Write-Host ""
    Write-Host "--- Inspecting $container ---" -ForegroundColor Cyan
    docker inspect $container | Select-String -Pattern "Health" -Context 0,10
}

Write-Host ""
Write-Host "🌐 Testing network connectivity..." -ForegroundColor Yellow

# Test if frontend is accessible
Write-Host "Testing frontend accessibility..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 10 -ErrorAction Stop
    Write-Host "✅ Frontend is accessible" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend is not accessible" -ForegroundColor Red
}

# Test if Ollama API is responsive
Write-Host "Testing Ollama API..." -ForegroundColor Yellow
try {
    $ollamaResponse = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 10 -ErrorAction Stop
    Write-Host "✅ Ollama API is responsive" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama API is not responsive" -ForegroundColor Red
}

Write-Host ""
Write-Host "📊 Resource usage:" -ForegroundColor Yellow
docker stats --no-stream

Write-Host ""
Write-Host "💡 Suggested fixes:" -ForegroundColor Cyan
Write-Host "1. Increase health check intervals in docker-compose.yml" -ForegroundColor White
Write-Host "2. Check if required environment variables are set" -ForegroundColor White
Write-Host "3. Verify volume mounts are working correctly" -ForegroundColor White
Write-Host "4. Ensure adequate system resources (CPU/RAM)" -ForegroundColor White
Write-Host "5. Check container logs for specific error messages" -ForegroundColor White