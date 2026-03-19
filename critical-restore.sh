#!/bin/bash
# CRITICAL: Emergency Service Restoration Script
# This script must be run ON THE VPS to restore services immediately

echo "🚨 EMERGENCY SERVICE RESTORATION INITIATED"
echo "=========================================="

# Check current docker status
echo "📊 Checking current Docker status..."
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check if containers are running but not responding
echo "🔍 Checking container health..."
docker inspect ai-factory-frontend --format='{{.State.Running}}' 2>/dev/null || echo "Frontend container not found"
docker inspect ai-factory-backend --format='{{.State.Running}}' 2>/dev/null || echo "Backend container not found"
docker inspect nginx --format='{{.State.Running}}' 2>/dev/null || echo "Nginx container not found"

# Force recreate all containers with latest configuration
echo "🔄 FORCE RECREATING ALL CONTAINERS..."

# Stop all containers
echo "🛑 Stopping all containers..."
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true

# Pull latest images
echo "📥 Pulling latest images..."
docker pull revanth2245/aisoftwarefactory-backend:staging
docker pull revanth2245/aisoftwarefactory-frontend:staging
docker pull nginx:alpine
docker pull postgres:15-alpine
docker pull redis:7-alpine
docker pull ollama/ollama:latest

# Create network if it doesn't exist
docker network create ai-factory-network 2>/dev/null || true

# Start infrastructure services
echo "🏗️ Starting infrastructure services..."

# PostgreSQL
docker run -d \
  --name postgres \
  --network ai-factory-network \
  --restart unless-stopped \
  -e POSTGRES_USER=aifactory \
  -e POSTGRES_PASSWORD=Itslogical1. \
  -e POSTGRES_DB=aifactory \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

# Redis
docker run -d \
  --name redis \
  --network ai-factory-network \
  --restart unless-stopped \
  -v redis_data:/data \
  redis:7-alpine

# Ollama
docker run -d \
  --name ollama \
  --network ai-factory-network \
  --restart unless-stopped \
  -p 11434:11434 \
  -v ollama_data:/root/.ollama \
  ollama/ollama:latest

# Wait for infrastructure
echo "⏳ Waiting for infrastructure services..."
sleep 15

# Start application services
echo "🚀 Starting application services..."

# Backend
docker run -d \
  --name ai-factory-backend \
  --network ai-factory-network \
  --restart unless-stopped \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e LOG_LEVEL=info \
  -e DATABASE_URL=postgresql://aifactory:Itslogical1.@postgres:5432/aifactory \
  -e REDIS_URL=redis://redis:6379 \
  -e OLLAMA_URL=http://ollama:11434 \
  -e SECRET_KEY=your-secret-key-change-in-production \
  -v backend_data:/app/data \
  revanth2245/aisoftwarefactory-backend:staging

# Frontend
docker run -d \
  --name ai-factory-frontend \
  --network ai-factory-network \
  --restart unless-stopped \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000/api \
  revanth2245/aisoftwarefactory-frontend:staging

# Wait for applications to start
echo "⏳ Waiting for applications to start..."
sleep 20

# Create and apply nginx configuration
echo "🌐 Configuring nginx reverse proxy..."

cat > /tmp/nginx-config.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server ai-factory-frontend:3000;
    }
    
    upstream backend {
        server ai-factory-backend:8000;
    }
    
    server {
        listen 80;
        server_name ai-staging.thetalogics.com localhost;
        
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
        
        location /api/ {
            proxy_pass http://backend/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        location /health {
            proxy_pass http://backend/health;
            proxy_set_header Host $host;
        }
    }
}
EOF

# Start nginx with custom configuration
docker run -d \
  --name nginx \
  --network ai-factory-network \
  --restart unless-stopped \
  -p 80:80 \
  -v /tmp/nginx-config.conf:/etc/nginx/nginx.conf:ro \
  nginx:alpine

# Final verification
echo "✅ SERVICES RESTARTED - VERIFYING STATUS..."

sleep 10

echo "📊 Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo "🧪 Service Tests:"
# Test local connectivity
curl -s -o /dev/null -w "Frontend: %{http_code}\n" http://localhost:3000/ || echo "Frontend: FAILED"
curl -s -o /dev/null -w "Backend: %{http_code}\n" http://localhost:8000/health || echo "Backend: FAILED"
curl -s -o /dev/null -w "Nginx: %{http_code}\n" http://localhost/ || echo "Nginx: FAILED"

echo "🎉 EMERGENCY RESTORATION COMPLETE!"
echo "Please verify external access to https://ai-staging.thetalogics.com"