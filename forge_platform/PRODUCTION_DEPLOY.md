# ForgeTrace Control Center - Production Deployment Guide

## 🎯 Production Deployment to forgetrace.pro

This guide walks you through deploying ForgeTrace Control Center to production with your Hostinger DNS.

## Prerequisites

- ✅ Domain: forgetrace.pro (owned, DNS via Hostinger)
- ✅ OAuth Apps configured (GitHub & Google)
- ✅ AWS Account (for SES email)
- ✅ Stripe Account (BAMG STUDIO LLC)
- ✅ Server (VPS, AWS EC2, or similar)

## Step 1: Server Setup

### Option A: AWS EC2 (Recommended)

```bash
# Launch EC2 instance
# - Type: t3.medium (2 vCPU, 4GB RAM minimum)
# - OS: Ubuntu 22.04 LTS
# - Storage: 50GB SSD
# - Security Group: Allow ports 80, 443, 22

# SSH into server
ssh -i your-key.pem ubuntu@your-server-ip
```

### Option B: Any VPS (DigitalOcean, Linode, etc.)

```bash
# Create droplet/instance
# - 4GB RAM minimum
# - Ubuntu 22.04 LTS
# - 50GB SSD

# SSH into server
ssh root@your-server-ip
```

## Step 2: Install Dependencies

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Verify installations
docker --version
docker-compose --version
nginx -v
```

## Step 3: Clone Repository

```bash
# Clone repo
git clone https://github.com/BAMG-Studio/ForgeTrace.git
cd ForgeTrace/forge_platform
```

## Step 4: Configure Environment

### Backend Configuration

```bash
# Copy production env
cp backend/.env.production backend/.env

# Edit with your values
nano backend/.env
```

**Update these critical values:**

```env
# Security - GENERATE NEW KEYS!
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# Database - Use strong password
DATABASE_URL=postgresql+asyncpg://forgetrace:STRONG_PASSWORD_HERE@postgres:5432/forgetrace_platform

# OAuth - Add your credentials
GITHUB_CLIENT_ID=<YOUR_GITHUB_CLIENT_ID>
GITHUB_CLIENT_SECRET=<YOUR_GITHUB_CLIENT_SECRET>
GITHUB_REDIRECT_URI=https://api.forgetrace.pro/api/v1/auth/callback/github

GOOGLE_CLIENT_ID=<YOUR_GOOGLE_CLIENT_ID>
GOOGLE_CLIENT_SECRET=<YOUR_GOOGLE_CLIENT_SECRET>
GOOGLE_REDIRECT_URI=https://api.forgetrace.pro/api/v1/auth/callback/google

# AWS - Add your credentials
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here

# Stripe - Add your keys
STRIPE_SECRET_KEY=sk_live_your_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret

# Domains
FRONTEND_URL=https://app.forgetrace.pro
API_URL=https://api.forgetrace.pro
PUBLIC_URL=https://www.forgetrace.pro
```

### Frontend Configuration

```bash
# Copy production env
cp frontend/.env.production frontend/.env

# Should contain:
VITE_API_URL=https://api.forgetrace.pro
VITE_APP_NAME=ForgeTrace
VITE_ENABLE_OAUTH=true
```

## Step 5: Update OAuth Callback URLs

### GitHub OAuth App

1. Go to: https://github.com/settings/applications/3270734
2. Update Authorization callback URL to:
   ```
   https://api.forgetrace.pro/api/v1/auth/callback/github
   ```
3. Save changes

### Google OAuth App

1. Go to: https://console.cloud.google.com/auth/clients?project=bamg-management-login
2. Edit "BAMG Management Login"
3. Update Authorized redirect URIs to:
   ```
   https://api.forgetrace.pro/api/v1/auth/callback/google
   ```
4. Save changes

## Step 6: Configure DNS (Hostinger)

Log into Hostinger DNS management and add these A records:

```
Type    Name    Value               TTL
A       @       YOUR_SERVER_IP      3600
A       www     YOUR_SERVER_IP      3600
A       app     YOUR_SERVER_IP      3600
A       api     YOUR_SERVER_IP      3600
```

Wait 5-10 minutes for DNS propagation. Verify:

```bash
dig forgetrace.pro
dig www.forgetrace.pro
dig app.forgetrace.pro
dig api.forgetrace.pro
```

## Step 7: Get SSL Certificates

```bash
# Stop nginx temporarily
sudo systemctl stop nginx

# Get certificates for all domains
sudo certbot certonly --standalone \
  -d forgetrace.pro \
  -d www.forgetrace.pro \
  -d app.forgetrace.pro \
  -d api.forgetrace.pro \
  --email hello@bamgstudio.com \
  --agree-tos

# Certificates will be in:
# /etc/letsencrypt/live/forgetrace.pro/
```

## Step 8: Configure Nginx

```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/forgetrace
```

Paste this configuration:

```nginx
# API Backend
server {
    listen 80;
    server_name api.forgetrace.pro;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.forgetrace.pro;

    ssl_certificate /etc/letsencrypt/live/forgetrace.pro/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/forgetrace.pro/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# App Frontend
server {
    listen 80;
    server_name app.forgetrace.pro;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.forgetrace.pro;

    ssl_certificate /etc/letsencrypt/live/forgetrace.pro/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/forgetrace.pro/privkey.pem;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Public Website (placeholder)
server {
    listen 80;
    server_name www.forgetrace.pro forgetrace.pro;
    return 301 https://www.forgetrace.pro$request_uri;
}

server {
    listen 443 ssl http2;
    server_name www.forgetrace.pro forgetrace.pro;

    ssl_certificate /etc/letsencrypt/live/forgetrace.pro/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/forgetrace.pro/privkey.pem;

    root /var/www/forgetrace;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

Enable the site:

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/forgetrace /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

## Step 9: Deploy Application

```bash
# Deploy
./deploy.sh production

# This will:
# - Build Docker containers
# - Start PostgreSQL and Redis
# - Run database migrations
# - Start backend API
# - Start frontend app
```

## Step 10: Create Super Admin

```bash
# Create super admin user
docker-compose exec backend python cli.py create-user \
  --email admin@forgetrace.pro \
  --password YOUR_SECURE_PASSWORD \
  --name "System Administrator" \
  --role super_admin
```

## Step 11: Verify Deployment

### Test Backend API

```bash
curl https://api.forgetrace.pro/health
# Should return: {"status":"healthy","version":"1.0.0","environment":"production"}
```

### Test Frontend

Visit: https://app.forgetrace.pro
- Should see login gateway
- Try both client and management sign-in

### Test OAuth

1. Visit https://app.forgetrace.pro
2. Click "Management Sign In"
3. Click "GitHub" or "Google"
4. Should redirect to OAuth provider
5. After authorization, should redirect back to dashboard

## Step 12: Set Up Monitoring

### CloudWatch (if using AWS)

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
```

### Basic Monitoring Script

```bash
# Create monitoring script
cat > /home/ubuntu/monitor.sh << 'EOF'
#!/bin/bash
# Check if services are running
docker-compose ps | grep -q "Up" || {
    echo "Services down! Restarting..."
    cd /home/ubuntu/ForgeTrace/forge_platform
    docker-compose restart
}
EOF

chmod +x /home/ubuntu/monitor.sh

# Add to crontab (check every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/ubuntu/monitor.sh") | crontab -
```

## Step 13: Set Up Backups

```bash
# Create backup script
cat > /home/ubuntu/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/home/ubuntu/backups

mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T postgres pg_dump -U forgetrace forgetrace_platform | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: db_$DATE.sql.gz"
EOF

chmod +x /home/ubuntu/backup.sh

# Run daily at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/backup.sh") | crontab -
```

## Step 14: Configure Firewall

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

## Step 15: SSL Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically sets up renewal cron job
# Verify it's there:
sudo systemctl status certbot.timer
```

## 🎉 Deployment Complete!

Your ForgeTrace Control Center is now live at:

- **Public Site**: https://www.forgetrace.pro
- **App Dashboard**: https://app.forgetrace.pro
- **API**: https://api.forgetrace.pro
- **API Docs**: https://api.forgetrace.pro/api/docs

## 📊 Post-Deployment Checklist

- [ ] All domains resolve correctly
- [ ] SSL certificates valid
- [ ] Backend API responding
- [ ] Frontend loading
- [ ] OAuth login works (GitHub)
- [ ] OAuth login works (Google)
- [ ] Email/password login works
- [ ] API token authentication works
- [ ] Database backups running
- [ ] Monitoring in place
- [ ] Firewall configured

## 🔧 Maintenance Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Update application
git pull
./deploy.sh production

# Create new user
docker-compose exec backend python cli.py create-user

# Create API token
docker-compose exec backend python cli.py create-token --email user@example.com

# Database backup (manual)
./backup.sh
```

## 🆘 Troubleshooting

### Services won't start
```bash
docker-compose down
docker-compose up -d
docker-compose logs -f
```

### OAuth not working
- Verify callback URLs in OAuth apps
- Check CORS settings in backend/.env
- Verify SSL certificates are valid

### Database connection issues
```bash
docker-compose restart postgres
sleep 5
docker-compose restart backend
```

## 📞 Support

- Email: hello@bamgstudio.com
- Documentation: /docs folder
- GitHub: https://github.com/BAMG-Studio/ForgeTrace

---

**Built by Peter Kolawole, BAMG Studio LLC**
