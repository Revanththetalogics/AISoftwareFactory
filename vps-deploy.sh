#!/bin/bash
echo "=== Setting up SSL and Deployment for ai-staging.thetalogics.com ==="

cd ~/ai-software-factory

# Create .env file
cat > .env << 'ENVFILE'
POSTGRES_PASSWORD=AiFactory2026Secure!
GITHUB_REPOSITORY=yourusername/aisoftwarefactory
ENVFILE

echo "[1/5] Installing Certbot..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

echo "[2/5] Opening firewall for HTTP/HTTPS..."
sudo ufw allow 'Nginx Full'

echo "[3/5] Creating temporary nginx config for SSL certificate generation..."
cat > nginx/nginx-temp.conf << 'NGINXCONF'
events {
    worker_connections 1024;
}
http {
    server {
        listen 80;
        server_name ai-staging.thetalogics.com;
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        location / {
            return 200 "OK";
        }
    }
}
NGINXCONF

echo "[4/5] Starting temporary nginx for SSL validation..."
docker run -d --name nginx-temp -p 80:80 \
  -v ~/ai-software-factory/nginx/nginx-temp.conf:/etc/nginx/nginx.conf:ro \
  -v ~/ai-software-factory/certbot/www:/var/www/certbot \
  nginx:alpine

echo "[5/5] Obtaining SSL certificate..."
sudo certbot certonly --standalone \
  --preferred-challenges http \
  -d ai-staging.thetalogics.com \
  --agree-tos \
  --non-interactive \
  --email admin@thetalogics.com

# Stop temporary nginx
docker stop nginx-temp
docker rm nginx-temp

echo ""
echo "=== SSL Certificate Obtained ==="
sudo ls -la /etc/letsencrypt/live/ai-staging.thetalogics.com/

echo ""
echo "=== Starting AI Software Factory ==="
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "=== Deployment Complete ==="
echo "Your AI Software Factory is now running at:"
echo "https://ai-staging.thetalogics.com"
echo ""
echo "Note: It may take a few minutes for all services to start."
