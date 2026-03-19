# AI Software Factory - Individual Service Deployment Script (PowerShell)
# Deploys services in groups to avoid Portainer stack size limitations

Write-Host "🚀 Starting AI Software Factory Deployment" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Load environment variables
$envFilePath = ".env.portainer.vps"
if (Test-Path $envFilePath) {
    Get-Content $envFilePath | ForEach-Object {
        if ($_ -match "^([^#=]+)=(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
    Write-Host "✅ Loaded environment variables from $envFilePath" -ForegroundColor Green
} else {
    Write-Host "❌ Error: $envFilePath file not found" -ForegroundColor Red
    exit 1
}

# Function to deploy a service group
function Deploy-ServiceGroup {
    param(
        [string]$ComposeFile,
        [string]$GroupName
    )
    
    Write-Host "📦 Deploying $GroupName..." -ForegroundColor Yellow
    
    $cmd = "docker-compose --env-file .env.portainer.vps -f $ComposeFile up -d"
    $result = Invoke-Expression $cmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $GroupName deployed successfully" -ForegroundColor Green
        
        # Wait for services to be healthy
        Write-Host "⏳ Waiting for services to become healthy..." -ForegroundColor Cyan
        Start-Sleep -Seconds 30
        
        # Show running containers for this group
        Write-Host "📋 Running containers in $GroupName:" -ForegroundColor Cyan
        docker-compose --env-file .env.portainer.vps -f $ComposeFile ps
        Write-Host ""
    } else {
        Write-Host "❌ Failed to deploy $GroupName" -ForegroundColor Red
        return $false
    }
    return $true
}

# Deploy in order: Core → App → Infra
Write-Host "1️⃣ Deploying Core Services (PostgreSQL, Redis, Ollama)..." -ForegroundColor Cyan
$coreSuccess = Deploy-ServiceGroup "core-services.yml" "Core Services"

Write-Host "2️⃣ Deploying Application Services (Backend, Frontend)..." -ForegroundColor Cyan
$appSuccess = Deploy-ServiceGroup "app-services.yml" "Application Services"

Write-Host "3️⃣ Deploying Infrastructure Services (Nginx, Cockpit, Watchtower)..." -ForegroundColor Cyan
$infraSuccess = Deploy-ServiceGroup "infra-services.yml" "Infrastructure Services"

# Final status check
Write-Host "🎯 Deployment Complete!" -ForegroundColor Green
Write-Host "=======================" -ForegroundColor Green
Write-Host "Services deployed:" -ForegroundColor White
Write-Host "  📊 Core Services: PostgreSQL, Redis, Ollama" -ForegroundColor White
Write-Host "  🚀 App Services: Backend API, Frontend" -ForegroundColor White
Write-Host "  🔧 Infra Services: Nginx, Cockpit, Watchtower, Backup" -ForegroundColor White
Write-Host ""
Write-Host "Access your application at: http://$($env:DOMAIN)" -ForegroundColor Yellow
Write-Host "Monitor system at: http://$($env:DOMAIN):9090 (Cockpit)" -ForegroundColor Yellow
Write-Host "API documentation: http://$($env:DOMAIN)/api/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "📊 Checking overall service status..." -ForegroundColor Cyan

docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-String -Pattern "(postgres|redis|ollama|backend|frontend|nginx|cockpit)"

Write-Host ""
Write-Host "✅ AI Software Factory deployment completed successfully!" -ForegroundColor Green