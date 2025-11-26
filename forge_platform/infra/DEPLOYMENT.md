# ForgeTrace Deployment Guide

## 🚀 Quick Start: Deploy to forgetrace.pro

### Prerequisites
- VPS access: `root@148.230.94.85`
- Domain: `forgetrace.pro` pointed to `148.230.94.85`
- Local machine with `rsync`, `ssh`, `npm`, `python3`

### Option 1: Password-less Deployment (Recommended)

```bash
# 1. Setup SSH keys (one-time)
chmod +x scripts/setup_ssh_keys.sh
./scripts/setup_ssh_keys.sh

# 2. Deploy
chmod +x scripts/deploy_to_vps.sh
./scripts/deploy_to_vps.sh
```

### Option 2: Manual Deployment with Password

```bash
# Deploy (will prompt for password 2-3 times)
chmod +x scripts/deploy_to_vps.sh
./scripts/deploy_to_vps.sh
```

### Post-Deployment: Enable HTTPS

SSH into your VPS and run:

```bash
ssh root@148.230.94.85
sudo certbot --nginx -d forgetrace.pro -d www.forgetrace.pro --email your@email.com --agree-tos --non-interactive
```

---

## 🔧 Manual Deployment Steps

If you prefer to deploy manually:

### 1. Build Frontend Locally

```bash
cd forge_platform/frontend
npm install
npm run build
```

### 2. Sync to VPS

```bash
rsync -avz --delete \
  --exclude='.venv' \
  --exclude='node_modules' \
  --exclude='.git' \
  ./ root@148.230.94.85:/opt/forgetrace/
```

### 3. Setup Backend on VPS

SSH into VPS:

```bash
ssh root@148.230.94.85
```

Run on VPS:

```bash
cd /opt/forgetrace

# Install dependencies
apt-get update
apt-get install -y python3 python3-venv nginx certbot python3-certbot-nginx

# Setup Python
python3 -m venv .venv
source .venv/bin/activate
# Root requirements (CLI/ML)
pip install -r requirements.txt
# Backend requirements (FastAPI/Uvicorn)
pip install -r forge_platform/backend/requirements.txt

# Create systemd service
cat > /etc/systemd/system/forgetrace-backend.service << 'EOF'
[Unit]
Description=ForgeTrace Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/forgetrace/forge_platform/backend
Environment="PATH=/opt/forgetrace/.venv/bin"
ExecStart=/opt/forgetrace/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
systemctl daemon-reload
systemctl enable forgetrace-backend
systemctl start forgetrace-backend
```

### 4. Configure Nginx

```bash
# On VPS
cat > /etc/nginx/sites-available/forgetrace << 'EOF'
server {
    listen 80;
    server_name forgetrace.pro www.forgetrace.pro;

    # Serve SPA from /app/
    location /app/ {
        root /opt/forgetrace/forge_platform/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Redirect root to /app/
    location = / {
        return 302 /app/;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

ln -s /etc/nginx/sites-available/forgetrace /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

---

## 🐳 Docker Deployment (Alternative)

### Build Images

```bash
# Build frontend
docker build -t forgetrace-frontend:latest -f forge_platform/frontend/Dockerfile forge_platform/frontend

# Build backend
docker build -t forgetrace-backend:latest -f forge_platform/backend/Dockerfile forge_platform/backend
```

### Run with Docker Compose

```bash
cd forge_platform/infra/docker
docker-compose up -d
```

---

## ☸️ Kubernetes Deployment

### Using kubectl

```bash
# Set your registry
export REGISTRY="your-registry.azurecr.io"  # or ghcr.io/bamg-studio
export VERSION="v1.0.0"

# Apply manifests
cd forge_platform/infra/k8s
envsubst < frontend-deployment.yaml | kubectl apply -f -
envsubst < backend-deployment.yaml | kubectl apply -f -
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml
```

### Using Kustomize

```bash
cd forge_platform/infra/k8s
kustomize edit set image forgetrace-frontend=your-registry/forgetrace-frontend:latest
kustomize edit set image forgetrace-backend=your-registry/forgetrace-backend:latest
kubectl apply -k .
```

---

## 🔍 Troubleshooting

### Check Backend Logs

```bash
# On VPS
journalctl -u forgetrace-backend -f
```

### Check Nginx Logs

```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Test Backend Directly

```bash
curl http://localhost:8000/health
```

### Restart Services

```bash
systemctl restart forgetrace-backend
systemctl reload nginx
```

---

## 📊 Monitoring

### Service Status

```bash
systemctl status forgetrace-backend
systemctl status nginx
```

### Resource Usage

```bash
htop
df -h
free -h
```

---

## 🔐 Security Checklist

- [ ] SSH key authentication enabled
- [ ] Password authentication disabled in `/etc/ssh/sshd_config`
- [ ] Firewall configured (UFW): `ufw allow 80,443/tcp`
- [ ] SSL certificates installed via Certbot
- [ ] Environment variables secured in `.env` file
- [ ] Database passwords rotated
- [ ] Backups configured

---

## 📝 Environment Variables

Create `/opt/forgetrace/.env` on VPS:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/forgetrace
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# AWS (for S3 storage)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_DEFAULT_REGION=us-east-1

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5050
```

---

## 🎯 Production Checklist

- [ ] Domain DNS configured
- [ ] SSL certificates installed
- [ ] Backend service running
- [ ] Nginx serving frontend
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] Monitoring setup
- [ ] Backups configured
- [ ] Log rotation configured
- [ ] Firewall rules applied
