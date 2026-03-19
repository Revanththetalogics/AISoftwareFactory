#!/bin/bash
# AI Software Factory - Individual Service Deployment Script
# Deploys services in groups to avoid Portainer stack size limitations

set -e

echo "🚀 Starting AI Software Factory Deployment"
echo "========================================="

# Load environment variables
if [ -f ".env.portainer.vps" ]; then
    export $(cat .env.portainer.vps | xargs)
    echo "✅ Loaded environment variables from .env.portainer.vps"
else
    echo "❌ Error: .env.portainer.vps file not found"
    exit 1
fi

# Function to deploy a service group
deploy_service_group() {
    local compose_file=$1
    local group_name=$2
    
    echo "📦 Deploying $group_name..."
    
    if docker-compose --env-file .env.portainer.vps -f $compose_file up -d; then
        echo "✅ $group_name deployed successfully"
        
        # Wait for services to be healthy
        echo "⏳ Waiting for services to become healthy..."
        sleep 30
        
        # Show running containers for this group
        echo "📋 Running containers in $group_name:"
        docker-compose --env-file .env.portainer.vps -f $compose_file ps
        echo ""
    else
        echo "❌ Failed to deploy $group_name"
        return 1
    fi
}

# Deploy in order: Core → App → Infra
echo "1️⃣ Deploying Core Services (PostgreSQL, Redis, Ollama)..."
deploy_service_group "core-services.yml" "Core Services"

echo "2️⃣ Deploying Application Services (Backend, Frontend)..."
deploy_service_group "app-services.yml" "Application Services"

echo "3️⃣ Deploying Infrastructure Services (Nginx, Cockpit, Watchtower)..."
deploy_service_group "infra-services.yml" "Infrastructure Services"

# Final status check
echo "🎯 Deployment Complete!"
echo "======================="
echo "Services deployed:"
echo "  📊 Core Services: PostgreSQL, Redis, Ollama"
echo "  🚀 App Services: Backend API, Frontend"
echo "  🔧 Infra Services: Nginx, Cockpit, Watchtower, Backup"
echo ""
echo "Access your application at: http://${DOMAIN}"
echo "Monitor system at: http://${DOMAIN}:9091 (cAdvisor)"
echo "API documentation: http://${DOMAIN}/api/docs"
echo ""
echo "📊 Checking overall service status..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(postgres|redis|ollama|backend|frontend|nginx|cockpit)"

echo ""
echo "✅ AI Software Factory deployment completed successfully!"