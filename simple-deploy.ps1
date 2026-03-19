# Simple Windows Deployment Script for Portainer
# Avoids complex volume mounting issues

Write-Host "🚀 Starting AI Software Factory Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Create necessary directories
Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "ssl\certs", "logs\nginx", "backups" -Force | Out-Null

# Generate self-signed certificate using PowerShell
Write-Host "🔐 Generating SSL certificates..." -ForegroundColor Yellow

# Create certificate directory
New-Item -ItemType Directory -Path "ssl" -Force | Out-Null

# Generate self-signed certificate
$cert = New-SelfSignedCertificate -DnsName "ai-staging.thetalogics.com" -CertStoreLocation "Cert:\CurrentUser\My" -KeyLength 2048 -KeyAlgorithm RSA
$certPath = "Cert:\CurrentUser\My\$($cert.Thumbprint)"

# Export certificate and key
$securePassword = ConvertTo-SecureString -String "password" -Force -AsPlainText
Export-PfxCertificate -Cert $certPath -FilePath "ssl\cert.pfx" -Password $securePassword | Out-Null

# Create placeholder certificate files for nginx
"# Self-signed certificate placeholder
# Replace with proper Let's Encrypt certificates for production" | Out-File -FilePath "ssl\certs\fullchain.pem" -Encoding ASCII

"# Private key placeholder
# Replace with proper Let's Encrypt certificates for production" | Out-File -FilePath "ssl\certs\privkey.pem" -Encoding ASCII

Write-Host "🐳 Deploying stack via Docker Compose..." -ForegroundColor Yellow
docker-compose -f docker-compose.portainer.yml up -d

Write-Host "⏱️ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "📋 Checking deployment status..." -ForegroundColor Yellow
docker-compose -f docker-compose.portainer.yml ps

Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host "Access your application at: http://66.70.191.79" -ForegroundColor Cyan
Write-Host "(Note: Using IP address since domain SSL setup requires additional configuration)" -ForegroundColor Yellow