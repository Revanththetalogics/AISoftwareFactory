#!/bin/bash
# VPS Hardening and GUI Management Setup Script

echo "=== Starting VPS Security Hardening & GUI Setup ==="

# Update system
echo "[1/10] Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential tools
echo "[2/10] Installing essential tools..."
sudo apt install -y curl wget git htop ncdu tree ufw fail2ban unattended-upgrades apt-listchanges

# Configure UFW Firewall
echo "[3/10] Configuring UFW firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 9090/tcp
sudo ufw allow 19999/tcp
sudo ufw allow 9443/tcp
sudo ufw --force enable

# Configure fail2ban
echo "[4/10] Setting up fail2ban..."
sudo tee /etc/fail2ban/jail.local > /dev/null << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
EOF
sudo systemctl enable fail2ban
sudo systemctl restart fail2ban

# Configure automatic security updates
echo "[5/10] Configuring automatic security updates..."
sudo tee /etc/apt/apt.conf.d/50unattended-upgrades > /dev/null << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::InstallOnShutdown "false";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

sudo tee /etc/apt/apt.conf.d/20auto-upgrades > /dev/null << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF

sudo systemctl enable unattended-upgrades
sudo systemctl restart unattended-upgrades

# Install Cockpit
echo "[6/10] Installing Cockpit web management..."
sudo apt install -y cockpit cockpit-pcp
sudo systemctl enable cockpit.socket

# Install Docker
echo "[7/10] Installing Docker..."
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
sudo systemctl enable docker

# Install Netdata
echo "[8/10] Installing Netdata monitoring..."
wget -O /tmp/netdata-kickstart.sh https://my-netdata.io/kickstart.sh
sudo sh /tmp/netdata-kickstart.sh --stable-channel --disable-telemetry --non-interactive

# Install Portainer
echo "[9/10] Installing Portainer (Docker GUI)..."
sudo docker volume create portainer_data
sudo docker run -d -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest

# Create management scripts
echo "[10/10] Creating management scripts..."
mkdir -p ~/scripts

cat > ~/scripts/vps-status.sh << 'SCRIPT'
#!/bin/bash
echo "=== VPS Status Report ==="
echo "Date: $(date)"
echo ""
echo "--- System Info ---"
hostnamectl
echo ""
echo "--- Uptime ---"
uptime
echo ""
echo "--- Disk Usage ---"
df -h /
echo ""
echo "--- Memory Usage ---"
free -h
echo ""
echo "--- Active Services ---"
sudo systemctl is-active cockpit.socket fail2ban docker netdata
echo ""
echo "--- UFW Status ---"
sudo ufw status verbose
echo ""
echo "--- Fail2Ban Status ---"
sudo fail2ban-client status sshd
echo ""
echo "--- Docker Containers ---"
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
SCRIPT
chmod +x ~/scripts/vps-status.sh

cat > ~/scripts/backup.sh << 'SCRIPT'
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

echo "Creating backup: $DATE"
tar -czf $BACKUP_DIR/etc_backup_$DATE.tar.gz /etc/nginx /etc/ufw /etc/fail2ban 2>/dev/null || true
tar -czf $BACKUP_DIR/home_backup_$DATE.tar.gz /home/ubuntu/scripts /home/ubuntu/docker-compose.yml 2>/dev/null || true

ls -t $BACKUP_DIR/*.tar.gz | tail -n +11 | xargs -r rm
echo "Backup complete: $BACKUP_DIR"
SCRIPT
chmod +x ~/scripts/backup.sh

# Create docker-compose template
cat > ~/docker-compose.yml << 'COMPOSE'
version: '3.8'

services:
  ai-factory-backend:
    image: ai-software-factory-backend:latest
    container_name: ai-factory-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=info
    volumes:
      - ./data:/app/data
    networks:
      - ai-factory

  ai-factory-frontend:
    image: ai-software-factory-frontend:latest
    container_name: ai-factory-frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    networks:
      - ai-factory

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - ai-factory

  postgres:
    image: postgres:15-alpine
    container_name: postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: aifactory
      POSTGRES_PASSWORD: changeme_in_production
      POSTGRES_DB: aifactory
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - ai-factory

  redis:
    image: redis:7-alpine
    container_name: redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - ai-factory

volumes:
  ollama_data:
  postgres_data:
  redis_data:

networks:
  ai-factory:
    driver: bridge
COMPOSE

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Your VPS is now hardened and ready!"
echo ""
echo "--- Access URLs ---"
echo "Cockpit (Server Management):  https://66.70.191.79:9090"
echo "Netdata (Monitoring):         http://66.70.191.79:19999"
echo "Portainer (Docker GUI):       https://66.70.191.79:9443"
echo ""
echo "--- Management Scripts ---"
echo "Check status:  ~/scripts/vps-status.sh"
echo "Backup:        ~/scripts/backup.sh"
echo ""
echo "--- Security Features Enabled ---"
echo "✓ UFW Firewall (ports: 22, 80, 443, 9090, 19999, 9443)"
echo "✓ fail2ban (blocks brute-force after 3 failed attempts)"
echo "✓ Automatic security updates"
echo "✓ Docker installed and configured"
