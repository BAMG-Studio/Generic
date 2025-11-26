#!/bin/bash
set -e

##############################################################################
# ForgeTrace Production Deployment Script for forgetrace.pro
# VPS: 148.230.94.85
##############################################################################

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 ForgeTrace Production Deployment${NC}"
echo "=================================================="

# Configuration
VPS_IP="${VPS_IP:-148.230.94.85}"
VPS_USER="${VPS_USER:-root}"
DOMAIN="${DOMAIN:-forgetrace.pro}"
DEPLOY_PATH="/opt/forgetrace"

# Check prerequisites
echo -e "\n${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v rsync &> /dev/null; then
    echo -e "${RED}❌ rsync not found. Install with: sudo apt install rsync${NC}"
    exit 1
fi

if ! command -v ssh &> /dev/null; then
    echo -e "${RED}❌ ssh not found${NC}"
    exit 1
fi

# Test SSH connection
echo -e "\n${YELLOW}🔐 Testing SSH connection to ${VPS_IP}...${NC}"
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes ${VPS_USER}@${VPS_IP} exit 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Password authentication required or SSH keys not configured${NC}"
    echo -e "${YELLOW}   Attempting deployment with password prompt...${NC}"
fi

# Build frontend
echo -e "\n${YELLOW}🏗️  Building frontend...${NC}"
cd forge_platform/frontend
npm install
npm run build
cd ../..

# Sync files to VPS
echo -e "\n${YELLOW}📦 Syncing files to VPS...${NC}"
rsync -avz --delete \
  --exclude='.venv' \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='mlruns/' \
  --exclude='*.egg-info' \
  --exclude='.coverage' \
  --exclude='htmlcov/' \
  --progress \
  ./ ${VPS_USER}@${VPS_IP}:${DEPLOY_PATH}/

# Deploy on VPS
echo -e "\n${YELLOW}🚀 Deploying on VPS...${NC}"
ssh ${VPS_USER}@${VPS_IP} bash << 'ENDSSH'
set -e

echo "📍 Deploying ForgeTrace..."
cd /opt/forgetrace

# Update system
echo "📦 Installing system dependencies..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq \
    python3 \
    python3-venv \
  python3-pip \
  nginx \
  certbot \
  python3-certbot-nginx \
  nodejs \
  npm \
  git \
  curl \
  postgresql-client \
  redis-tools

# Setup Python environment
echo "🐍 Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
# Root requirements (CLI/ML)
pip install -r requirements.txt
# Backend requirements (FastAPI/Uvicorn/etc.)
pip install -r forge_platform/backend/requirements.txt
# Install local package
pip install -e .

# Setup systemd service for backend
echo "⚙️  Configuring backend service..."
cat > /etc/systemd/system/forgetrace-backend.service << 'SERVICE'
[Unit]
Description=ForgeTrace FastAPI Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/forgetrace/forge_platform/backend
Environment="PATH=/opt/forgetrace/.venv/bin"
Environment="PYTHONPATH=/opt/forgetrace:/opt/forgetrace/forge_platform/backend"
ExecStart=/opt/forgetrace/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# Setup Nginx configuration
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/forgetrace << 'NGINX'
# ForgeTrace Production Configuration
upstream backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name forgetrace.pro www.forgetrace.pro;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Frontend SPA served from /app/
    location /app/ {
        root /opt/forgetrace/forge_platform/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Long-cache hashed assets
    location ~* /app/assets/.*\.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)$ {
        root /opt/forgetrace/forge_platform/frontend/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Redirect bare root to /app/
    location = / {
        return 302 /app/;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_request_buffering off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
NGINX

# Enable site
ln -sf /etc/nginx/sites-available/forgetrace /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
nginx -t
systemctl reload nginx

# Start backend service
echo "🚀 Starting backend service..."
systemctl daemon-reload
systemctl enable forgetrace-backend
systemctl restart forgetrace-backend

# Wait for backend to start
sleep 5

# Check service status
if systemctl is-active --quiet forgetrace-backend; then
    echo "✅ Backend service started successfully"
else
    echo "❌ Backend service failed to start"
    journalctl -u forgetrace-backend -n 50 --no-pager
    exit 1
fi

echo ""
echo "=================================================="
echo "✅ Deployment Complete!"
echo "=================================================="
echo ""
echo "🌐 Site: http://forgetrace.pro"
echo "🔧 Backend: http://127.0.0.1:8000"
echo ""
echo "📊 Service Status:"
systemctl status forgetrace-backend --no-pager -l
echo ""
echo "🔐 To enable HTTPS, run on the VPS:"
echo "   sudo certbot --nginx -d forgetrace.pro -d www.forgetrace.pro"
echo ""

ENDSSH

echo -e "\n${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Update DNS: Point forgetrace.pro A record to ${VPS_IP}"
echo "2. Enable SSL: SSH to VPS and run: sudo certbot --nginx -d forgetrace.pro -d www.forgetrace.pro"
echo "3. Configure environment variables in /opt/forgetrace/.env"
echo ""
echo -e "${GREEN}🎉 ForgeTrace is now live at http://forgetrace.pro${NC}"
