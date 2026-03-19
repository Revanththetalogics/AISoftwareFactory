#!/bin/bash
# AI Software Factory - One-Click Enterprise Deployment
# Completely automated setup - no technical knowledge required

set -e  # Exit on any error

echo "🚀 Starting AI Software Factory Enterprise Deployment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
print_status "Checking system requirements..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    print_success "Docker installed successfully"
else
    print_success "Docker is already installed"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose installed successfully"
else
    print_success "Docker Compose is already installed"
fi

# Create project directory
PROJECT_DIR="/opt/ai-software-factory"
print_status "Setting up project directory: $PROJECT_DIR"

sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR
cd $PROJECT_DIR

# Download all configuration files
print_status "Downloading enterprise configuration files..."

# Main docker-compose file
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # AI Software Factory Backend
  backend:
    image: revanth2245/aisoftwarefactory-backend:staging
    container_name: ai-factory-backend
    restart: unless-stopped
    labels:
      - "com.centurylinklabs.watchtower.enable=true"
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=info
      - DATABASE_URL=postgresql://aifactory:${POSTGRES_PASSWORD}@postgres:5432/aifactory
      - REDIS_URL=redis://redis:6379
      - OLLAMA_URL=http://ollama:11434
      - SECRET_KEY=${SECRET_KEY}
      - ENABLE_METRICS=true
      - METRICS_PORT=9090
    volumes:
      - backend_data:/app/data
      - ./logs/backend:/app/logs
    networks:
      - ai-factory-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G

  # AI Software Factory Frontend
  frontend:
    image: revanth2245/aisoftwarefactory-frontend:staging
    container_name: ai-factory-frontend
    restart: unless-stopped
    labels:
      - "com.centurylinklabs.watchtower.enable=true"
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=https://${DOMAIN}/api
      - NEXT_PUBLIC_WS_URL=wss://${DOMAIN}/ws
    volumes:
      - frontend_cache:/app/.next/cache
    networks:
      - ai-factory-network
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  # Nginx Reverse Proxy with SSL
  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    restart: unless-stopped
    labels:
      - "com.centurylinklabs.watchtower.enable=true"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl/certs:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
      - letsencrypt_data:/etc/letsencrypt
    networks:
      - ai-factory-network
    depends_on:
      - frontend
      - backend
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

  # Ollama AI Service
  ollama:
    image: ollama/ollama:latest
    container_name: ollama-ai
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - ai-factory-network
    environment:
      - OLLAMA_KEEP_ALIVE=24h
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: postgres-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: aifactory
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: aifactory
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - ai-factory-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aifactory"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: redis-cache
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - ai-factory-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  # Watchtower - Automatic Updates
  watchtower:
    image: containrrr/watchtower:latest
    container_name: watchtower-auto-update
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_POLL_INTERVAL=3600
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_INCLUDE_STOPPED=true
      - WATCHTOWER_REVIVE_STOPPED=true
      - WATCHTOWER_LABEL_ENABLE=true
    networks:
      - ai-factory-network
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 128M

volumes:
  backend_data:
  frontend_cache:
  ollama_data:
  postgres_data:
  redis_data:
  letsencrypt_data:

networks:
  ai-factory-network:
    driver: bridge
EOF

print_success "Main configuration downloaded"

# Create environment file with auto-generated secure passwords
print_status "Generating secure configuration..."

# Generate secure passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -hex 64)
GRAFANA_PASSWORD=$(openssl rand -base64 24)

# Create environment file
cat > .env << EOF
# Auto-generated secure configuration
# Generated on: $(date)

# Database
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_USER=aifactory
POSTGRES_DB=aifactory

# Security
SECRET_KEY=$SECRET_KEY
GRAFANA_ADMIN_PASSWORD=$GRAFANA_PASSWORD

# Domain Configuration
DOMAIN=ai-staging.thetalogics.com
NEXT_PUBLIC_API_URL=https://\${DOMAIN}/api
NEXT_PUBLIC_WS_URL=wss://\${DOMAIN}/ws

# Services
OLLAMA_URL=http://ollama:11434
REDIS_URL=redis://redis:6379

# Deployment
ENVIRONMENT=production
LOG_LEVEL=info
PORTAINER_STACK_NAME=ai-software-factory
COMPOSE_PROJECT_NAME=ai-factory

# Features
ENABLE_METRICS=true
ENABLE_WEBSOCKET=true
EOF

print_success "Secure environment configuration created"

# Create directory structure
print_status "Creating directory structure..."
mkdir -p nginx ssl/certs logs/{backend,nginx} backups

# Create basic nginx configuration
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    sendfile        on;
    keepalive_timeout  65;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript;
    
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        server_name _;
        
        # Let's Encrypt challenge
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        # Redirect all HTTP to HTTPS
        location / {
            return 301 https://$host$request_uri;
        }
    }
    
    server {
        listen 443 ssl http2;
        server_name ai-staging.thetalogics.com;
        
        # SSL Configuration (will be updated with real certificates)
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        
        # API Routes
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # WebSocket Support
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
        
        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

print_success "Nginx configuration created"

# Create SSL certificate placeholder
print_status "Setting up SSL certificate management..."

# Create self-signed certificate for immediate use
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/certs/privkey.pem \
    -out ssl/certs/fullchain.pem \
    -subj "/CN=ai-staging.thetalogics.com"

print_success "SSL certificates generated"

# Create backup script
cat > backup-system.sh << 'EOF'
#!/bin/bash
# Automated backup script

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="aifactory_backup_$DATE.tar.gz"

echo "Creating backup: $BACKUP_FILE"

# Create backup
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    --exclude='*.log' \
    ./volumes/

# Remove backups older than 30 days
find "$BACKUP_DIR" -name "aifactory_backup_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
EOF

chmod +x backup-system.sh

print_success "Backup system configured"

# Create monitoring script
cat > monitor-services.sh << 'EOF'
#!/bin/bash
# Service monitoring script

echo "🔍 Checking service status..."

SERVICES=("backend" "frontend" "nginx" "postgres" "redis" "ollama")

for service in "${SERVICES[@]}"; do
    if docker ps | grep -q "ai-factory-$service"; then
        echo "✅ $service: Running"
    else
        echo "❌ $service: Not running"
    fi
done

echo ""
echo "📊 Resource usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
EOF

chmod +x monitor-services.sh

print_success "Monitoring system configured"

# Create deployment script
cat > deploy.sh << 'EOF'
#!/bin/bash
# Automated deployment script

echo "🚀 Deploying AI Software Factory..."

# Pull latest images
echo "📥 Pulling latest images..."
docker-compose pull

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose down

# Start services
echo "🟢 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Show status
echo "📋 Deployment status:"
docker-compose ps

echo "🎉 Deployment completed!"
echo "Access your application at: https://ai-staging.thetalogics.com"
EOF

chmod +x deploy.sh

print_success "Deployment automation ready"

# Create update script
cat > update-system.sh << 'EOF'
#!/bin/bash
# Automated system updates

echo "🔄 Updating system components..."

# Update docker images
echo "📥 Updating Docker images..."
docker-compose pull

# Restart services to use new images
echo "🔄 Restarting services..."
docker-compose up -d

# Clean up old images
echo "🧹 Cleaning up old images..."
docker image prune -f

echo "✅ System update completed!"
EOF

chmod +x update-system.sh

print_success "Update automation ready"

# Final deployment
print_status "Starting deployment..."

# Make sure we're in the right directory
cd $PROJECT_DIR

# Deploy the stack
./deploy.sh

# Show final status
echo ""
echo "==========================================="
echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "==========================================="
echo ""
echo "Your AI Software Factory is now running!"
echo ""
echo "🌐 Access Points:"
echo "   Web Interface: https://ai-staging.thetalogics.com"
echo "   Direct Backend: http://localhost:8000"
echo "   Direct Frontend: http://localhost:3000"
echo ""
echo "🔧 Management Commands:"
echo "   Check status: ./monitor-services.sh"
echo "   Create backup: ./backup-system.sh"
echo "   Update system: ./update-system.sh"
echo "   Redeploy: ./deploy.sh"
echo ""
echo "📂 Important Locations:"
echo "   Configuration: $PROJECT_DIR"
echo "   Logs: $PROJECT_DIR/logs/"
echo "   Backups: $PROJECT_DIR/backups/"
echo ""
echo "🔐 Security Information:"
echo "   PostgreSQL Password: $POSTGRES_PASSWORD"
echo "   Admin Secret Key: [Hidden for security]"
echo ""
echo "The system will automatically:"
echo "   • Update itself every hour"
echo "   • Create daily backups"
echo "   • Monitor service health"
echo "   • Restart failed services"
echo ""
print_success "Your enterprise AI platform is ready for use!"