# ForgeTrace Control Center - Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Prerequisites

- Docker & Docker Compose installed
- Git installed
- 8GB RAM minimum

### Step 1: Clone & Navigate

```bash
cd /home/papaert/projects/ForgeTrace/forge_platform
```

### Step 2: Deploy

```bash
# For development
./deploy.sh development

# For production
./deploy.sh production
```

That's it! The script will:
- ✅ Set up PostgreSQL database
- ✅ Set up Redis cache
- ✅ Run database migrations
- ✅ Create super admin user (dev only)
- ✅ Start all services

### Step 3: Access the Platform

**Frontend (Login Gateway)**
- URL: http://localhost:5173
- Try both Client and Management sign-in

**Backend API**
- URL: http://localhost:8000
- Docs: http://localhost:8000/api/docs

**Super Admin (Development Only)**
- Email: `admin@forgetrace.pro`
- Password: `admin123`

### Step 4: Test Authentication

#### Test Management Login (Email/Password)

1. Visit http://localhost:5173
2. Click "Management Sign In"
3. Enter credentials:
   - Email: `admin@forgetrace.pro`
   - Password: `admin123`
4. You should be redirected to the dashboard

#### Test OAuth Login (GitHub/Google)

1. Visit http://localhost:5173
2. Click "Management Sign In"
3. Click "GitHub" or "Google"
4. Authorize the application
5. You'll be redirected back to the dashboard

**Note:** For OAuth to work locally, you need to update the callback URLs in your OAuth apps:
- GitHub: http://localhost:8000/api/v1/auth/callback/github
- Google: http://localhost:8000/api/v1/auth/callback/google

#### Test Client Token Login

1. Create an API token:
```bash
docker-compose exec backend python cli.py create-token --email admin@forgetrace.pro
```

2. Copy the token (starts with `ftk_`)

3. Visit http://localhost:5173
4. Click "Client Sign In"
5. Paste the token
6. You should see the client portal

### Step 5: Explore the API

Visit http://localhost:8000/api/docs to see all available endpoints.

**Try these:**

```bash
# Health check
curl http://localhost:8000/health

# Register new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@forgetrace.pro&password=admin123"
```

## 🛠️ CLI Commands

The platform includes a CLI for management tasks:

```bash
# Create user
docker-compose exec backend python cli.py create-user

# Create API token
docker-compose exec backend python cli.py create-token --email user@example.com

# List all users
docker-compose exec backend python cli.py list-users

# List user's tokens
docker-compose exec backend python cli.py list-tokens --email user@example.com

# Revoke token
docker-compose exec backend python cli.py revoke-token --prefix ftk_xxxxxxxx
```

## 📊 View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Database only
docker-compose logs -f postgres
```

## 🔄 Restart Services

```bash
# Restart all
docker-compose restart

# Restart backend only
docker-compose restart backend
```

## 🛑 Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

## 🔧 Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Rebuild
docker-compose build backend
docker-compose up -d backend
```

### Database connection error

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres

# Wait a few seconds and restart backend
sleep 5
docker-compose restart backend
```

### Frontend can't connect to API

1. Check backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in `backend/.env`
3. Verify `VITE_API_URL` in `frontend/.env`

### OAuth not working

1. Verify OAuth credentials in `backend/.env`
2. Check callback URLs match:
   - GitHub: http://localhost:8000/api/v1/auth/callback/github
   - Google: http://localhost:8000/api/v1/auth/callback/google
3. Make sure OAuth apps are enabled

## 🚀 Production Deployment

### Update OAuth Callback URLs

For production, update your OAuth apps:

**GitHub:**
- Callback URL: https://api.forgetrace.pro/api/v1/auth/callback/github

**Google:**
- Authorized redirect URI: https://api.forgetrace.pro/api/v1/auth/callback/google

### Update Environment Files

1. Edit `backend/.env.production`:
   - Change `SECRET_KEY` and `JWT_SECRET` to strong random values
   - Add your AWS credentials
   - Add your Stripe keys
   - Update domain URLs

2. Edit `frontend/.env.production`:
   - Set `VITE_API_URL=https://api.forgetrace.pro`

### Deploy

```bash
./deploy.sh production
```

### Configure DNS

Point your domains to your server:
```
www.forgetrace.pro    → Your server IP
app.forgetrace.pro    → Your server IP
api.forgetrace.pro    → Your server IP
```

### Set Up SSL

Use Let's Encrypt with Certbot:

```bash
# Install certbot
sudo apt-get install certbot

# Get certificates
sudo certbot certonly --standalone -d forgetrace.pro -d www.forgetrace.pro -d app.forgetrace.pro -d api.forgetrace.pro
```

### Configure Nginx (if not using Docker)

See `infra/docker/nginx.conf` for configuration example.

## 📚 Next Steps

1. **Customize branding** - Update logos and colors in frontend
2. **Add email templates** - Configure AWS SES for notifications
3. **Set up monitoring** - Add CloudWatch or similar
4. **Configure backups** - Automate database backups
5. **Add payment processing** - Integrate Stripe subscriptions
6. **Deploy mobile apps** - Build iOS and Android apps

## 🆘 Need Help?

- **Documentation**: See `docs/` folder
- **Email**: hello@bamgstudio.com
- **GitHub Issues**: https://github.com/BAMG-Studio/ForgeTrace/issues

## 🎉 You're Ready!

Your ForgeTrace Control Center is now running. Start building amazing IP audit workflows!
