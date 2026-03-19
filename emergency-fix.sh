#!/bin/bash
# Emergency Backend Fix Script
# Fixes uvicorn missing dependency issue

echo "🔧 Emergency Backend Container Fix"
echo "==================================="

# Stop the crashing backend container
echo "🛑 Stopping backend container..."
docker stop ai-factory-backend 2>/dev/null || echo "Container not running"

# Remove the container
echo "🗑️ Removing container..."
docker rm ai-factory-backend 2>/dev/null || echo "Container not present"

# Pull the latest image
echo "📥 Pulling latest backend image..."
docker pull revanth2245/aisoftwarefactory-backend:staging

# Create a temporary fix by installing uvicorn manually
echo "🛠️ Creating fixed container with uvicorn..."

# Run container with manual uvicorn installation
docker run -d \
  --name ai-factory-backend-temp \
  --restart unless-stopped \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e LOG_LEVEL=info \
  -e DATABASE_URL=postgresql://aifactory:${POSTGRES_PASSWORD}@postgres:5432/aifactory \
  -e REDIS_URL=redis://redis:6379 \
  -e OLLAMA_URL=http://ollama:11434 \
  -e SECRET_KEY=${SECRET_KEY} \
  -e ENABLE_METRICS=true \
  -e METRICS_PORT=9090 \
  -v backend_data:/app/data \
  -v $(pwd)/logs/backend:/app/logs \
  --network ai-factory-network \
  revanth2245/aisoftwarefactory-backend:staging \
  sh -c "pip install uvicorn && python main.py"

echo "⏱️ Waiting for container to start..."
sleep 30

# Check if container is running
if docker ps | grep -q ai-factory-backend-temp; then
    echo "✅ Temporary fix applied successfully!"
    echo "📦 Container is now running with uvicorn installed"
    
    # Rename container to original name
    echo "🔄 Renaming container..."
    docker rename ai-factory-backend-temp ai-factory-backend
    
    echo "📋 Checking container status..."
    docker ps | grep ai-factory-backend
    
    echo "🧪 Testing backend access..."
    sleep 10
    if curl -f http://localhost:8000/health 2>/dev/null; then
        echo "🎉 Backend is now accessible!"
    else
        echo "⚠️ Backend started but health check failed"
        echo "📋 Check logs: docker logs ai-factory-backend"
    fi
else
    echo "❌ Fix failed - checking logs..."
    docker logs ai-factory-backend-temp 2>/dev/null || echo "No logs available"
fi

echo ""
echo "💡 Next steps:"
echo "1. Update your backend Docker image to include uvicorn permanently"
echo "2. Rebuild and redeploy with proper dependencies"
echo "3. Consider using an official FastAPI/Uvicorn base image"