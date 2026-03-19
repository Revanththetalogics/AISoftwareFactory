#!/bin/bash
# Simple Portainer-Compatible Deployment Script
# Avoids complex volume mounting issues

echo "🚀 Starting AI Software Factory Deployment"
echo "=========================================="

# Create necessary directories
mkdir -p ssl/certs logs/nginx backups

# Generate a simple self-signed certificate for immediate use
echo "🔐 Generating SSL certificates..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/certs/privkey.pem \
    -out ssl/certs/fullchain.pem \
    -subj "/CN=ai-staging.thetalogics.com"

echo "🐳 Deploying stack via Docker Compose..."
docker-compose -f docker-compose.portainer.yml up -d

echo "⏱️ Waiting for services to start..."
sleep 30

echo "📋 Checking deployment status..."
docker-compose -f docker-compose.portainer.yml ps

echo "✅ Deployment completed!"
echo "Access your application at: https://ai-staging.thetalogics.com"
echo "(Note: You'll need to set up proper SSL certificates for production use)"