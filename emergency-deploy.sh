#!/bin/bash
# Emergency deployment script for AI Software Factory
# Run this on the VPS to manually deploy the latest configuration

echo "🚀 Starting emergency deployment..."

# Pull latest images
echo "📥 Pulling latest images..."
docker pull revanth2245/aisoftwarefactory-backend:staging
docker pull revanth2245/aisoftwarefactory-frontend:staging

# Stop and remove existing containers (except watchtower for now)
echo "🛑 Stopping containers..."
docker stop ai-factory-backend ai-factory-frontend nginx postgres redis ollama 2>/dev/null || true
docker rm ai-factory-backend ai-factory-frontend nginx postgres redis ollama 2>/dev/null || true

# Update nginx configuration file
echo "📋 Updating nginx configuration..."
cat > /tmp/nginx.conf << 'EOF'
# Primary server block - this should take precedence
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name ai-staging.thetalogics.com localhost _;

    # Proxy all requests to frontend container
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Handle WebSocket upgrades
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Ensure proper error handling
        proxy_intercept_errors on;
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Handle CORS
        proxy_set_header Origin "";
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Proxy WebSocket connections
    location /ws/ {
        proxy_pass http://backend:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://backend:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Error pages - fallback to frontend
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        proxy_pass http://frontend:3000;
    }
}

# Catch-all server block
server {
    listen 80;
    server_name _;
    return 301 https://ai-staging.thetalogics.com$request_uri;
}
EOF

# Copy nginx config to proper location
sudo cp /tmp/nginx.conf /etc/nginx/conf.d/00-ai-factory.conf
sudo rm -f /etc/nginx/conf.d/default.conf

# Start services in correct order
echo "🔄 Starting services..."

# Start infrastructure services first
docker run -d \
  --name postgres \
  --network ai-factory-network \
  -e POSTGRES_USER=aifactory \
  -e POSTGRES_PASSWORD=Itslogical1. \
  -e POSTGRES_DB=aifactory \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

docker run -d \
  --name redis \
  --network ai-factory-network \
  -v redis_data:/data \
  redis:7-alpine

docker run -d \
  --name ollama \
  --network ai-factory-network \
  -p 11434:11434 \
  -v ollama_data:/root/.ollama \
  ollama/ollama:latest

# Wait for infrastructure to be ready
sleep 10

# Start application services
docker run -d \
  --name ai-factory-backend \
  --network ai-factory-network \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e LOG_LEVEL=info \
  -e DATABASE_URL=postgresql://aifactory:Itslogical1.@postgres:5432/aifactory \
  -e REDIS_URL=redis://redis:6379 \
  -e OLLAMA_URL=http://ollama:11434 \
  -e SECRET_KEY=your-secret-key-change-in-production \
  -v backend_data:/app/data \
  revanth2245/aisoftwarefactory-backend:staging

docker run -d \
  --name ai-factory-frontend \
  --network ai-factory-network \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://ai-staging.thetalogics.com/api \
  revanth2245/aisoftwarefactory-frontend:staging

# Wait for applications to start
sleep 15

# Start nginx with our configuration
docker run -d \
  --name nginx \
  --network ai-factory-network \
  -p 80:80 \
  -v /etc/nginx/conf.d/00-ai-factory.conf:/etc/nginx/conf.d/default.conf:ro \
  nginx:alpine

echo "✅ Deployment completed!"
echo "🔍 Verifying services..."

# Check service status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test the deployment
echo "🧪 Testing deployment..."
curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "200" && echo "✅ Frontend accessible" || echo "❌ Frontend not accessible"
curl -s -o /dev/null -w "%{http_code}" http://localhost/api/v1/health | grep -q "200" && echo "✅ Backend API accessible" || echo "❌ Backend API not accessible"

echo "🎉 Emergency deployment finished!"