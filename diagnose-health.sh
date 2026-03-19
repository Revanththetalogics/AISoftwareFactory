#!/bin/bash
# Container Health Diagnostic Script

echo "🏥 Container Health Diagnostic"
echo "=============================="

echo "📋 Checking container statuses..."
docker-compose -f docker-compose.portainer.yml ps

echo ""
echo "🔍 Checking unhealthy containers..."
UNHEALTHY_CONTAINERS=$(docker-compose -f docker-compose.portainer.yml ps | grep unhealthy | awk '{print $1}')

if [ -z "$UNHEALTHY_CONTAINERS" ]; then
    echo "✅ All containers are healthy!"
    exit 0
fi

echo "⚠️  Unhealthy containers found:"
echo "$UNHEALTHY_CONTAINERS"

echo ""
echo "📝 Getting detailed logs for unhealthy containers..."

for container in $UNHEALTHY_CONTAINERS; do
    echo ""
    echo "--- Logs for $container ---"
    docker logs --tail 50 $container
    
    echo ""
    echo "--- Inspecting $container ---"
    docker inspect $container | grep -A 10 "Health"
done

echo ""
echo "🌐 Testing network connectivity..."

# Test if frontend is accessible
echo "Testing frontend accessibility..."
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not accessible"
fi

# Test if Ollama API is responsive
echo "Testing Ollama API..."
if curl -f http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "✅ Ollama API is responsive"
else
    echo "❌ Ollama API is not responsive"
fi

echo ""
echo "📊 Resource usage:"
docker stats --no-stream

echo ""
echo "💡 Suggested fixes:"
echo "1. Increase health check intervals in docker-compose.yml"
echo "2. Check if required environment variables are set"
echo "3. Verify volume mounts are working correctly"
echo "4. Ensure adequate system resources (CPU/RAM)"
echo "5. Check container logs for specific error messages"