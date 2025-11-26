#!/bin/bash
# Run this ON THE VPS after files are synced
set -e

echo "🚀 ForgeTrace VPS Setup Script"
echo "Run this on: root@148.230.94.85"
echo "================================"
echo ""

cd /opt/forgetrace

# Install system dependencies
echo "📦 Installing system dependencies..."
apt-get update -qq
apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
  nginx \
  certbot \
  python3-certbot-nginx \
  nodejs \
  npm \
  postgresql-client \
  redis-tools

# Setup Python environment
echo "🐍 Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
# Install root requirements (CLI, ML libs)
pip install -r requirements.txt
# Install backend requirements (FastAPI + Uvicorn, etc.)
pip install -r forge_platform/backend/requirements.txt
# Install local package in editable mode
pip install -e .

# Create systemd service
echo "⚙️  Creating backend service..."
cat > /etc/systemd/system/forgetrace-backend.service << 'EOF'
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
EOF

# Configure Nginx
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/forgetrace << 'EOF'
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

    # Frontend at /app
    location /app/ {
        root /opt/forgetrace/forge_platform/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Static assets (hashed) served long-cache regardless of path
    location ~* /app/assets/.*\.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2)$ {
        root /opt/forgetrace/forge_platform/frontend/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Optional redirect root -> /app/
    location = / {
        return 302 /app/;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/forgetrace /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
nginx -t && systemctl reload nginx

# Start backend
echo "🚀 Starting backend service..."
systemctl daemon-reload
systemctl enable forgetrace-backend
systemctl restart forgetrace-backend

# Wait and check
sleep 3
systemctl status forgetrace-backend --no-pager

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Your site: http://forgetrace.pro"
echo ""
echo "🔒 To enable HTTPS, run:"
echo "   certbot --nginx -d forgetrace.pro -d www.forgetrace.pro"
echo ""
