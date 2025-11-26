# 🚀 ForgeTrace Platform - Quick Reference Card

## 📍 Current Status

### ✅ All Services Running
```
✓ Backend API      http://localhost:8001       (FastAPI + PostgreSQL)
✓ Frontend         http://localhost:3001       (React + TypeScript)
✓ API Docs         http://localhost:8001/api/docs
✓ MLflow Server    http://localhost:5050       (Experiment tracking)
✓ Database         localhost:5433              (PostgreSQL 15)
✓ Redis Cache      localhost:6379              (Caching layer)
```

---

## ⚡ Quick Commands

### Start/Stop Services

```bash
# Backend
cd forge_platform/backend
/home/papaert/projects/ForgeTrace/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001

# MLflow
cd deployment/mlflow
docker-compose up -d       # Start
docker-compose down        # Stop
docker-compose restart     # Restart

# Database
cd forge_platform/infra/docker
docker-compose up -d postgres
```

### Test Authentication

```bash
# Login and get token
export TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bamgstudio.com","password":"SecurePass123!"}' \
  | jq -r '.access_token')

# Get user profile
curl http://localhost:8001/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN" | jq .
```

---

## 🔧 Configuration Files

### Backend Environment
**File:** `forge_platform/backend/.env`

**Required:**
- `SECRET_KEY` ✅ (configured)
- `JWT_SECRET` ✅ (configured)
- `DATABASE_URL` ✅ (configured)

**Optional (for production):**
- `AWS_ACCESS_KEY_ID` - For S3 storage
- `AWS_SECRET_ACCESS_KEY` - For S3 storage
- `GITHUB_CLIENT_ID` - For GitHub OAuth
- `GITHUB_CLIENT_SECRET` - For GitHub OAuth
- `GOOGLE_CLIENT_ID` - For Google OAuth
- `GOOGLE_CLIENT_SECRET` - For Google OAuth
- `MLFLOW_TRACKING_URI` ✅ (http://localhost:5050)

### Frontend Environment
**File:** `forge_platform/frontend/.env`
```bash
VITE_API_URL=http://localhost:8001/api/v1
```

---

## 🎯 Integration Setup Scripts

### 1. AWS S3 Setup
```bash
# Prerequisites: AWS CLI configured (aws configure)
./scripts/setup_aws.sh

# What it does:
# - Creates forgetrace-scans bucket
# - Creates forgetrace-models bucket
# - Enables versioning
# - Enables encryption
# - Sets lifecycle policies
```

### 2. OAuth Setup
```bash
./scripts/setup_oauth.sh

# What it does:
# - Interactive GitHub OAuth configuration
# - Interactive Google OAuth configuration
# - Updates backend/.env automatically
```

### 3. MLflow Already Running ✅
```bash
# Access at: http://localhost:5050
# Containers: forgetrace-mlflow, forgetrace-mlflow-db
```

### 4. Windows ↔ WSL Port Forward (if browser can’t reach localhost)
```bash
# From WSL (adds rules for MLflow 5050, API 8001, Frontend 3001)
./scripts/setup_portproxy.sh

# Or from Windows PowerShell (admin)
powershell -ExecutionPolicy Bypass -File scripts/setup_portproxy.ps1
```
Then open:
- MLflow: http://localhost:5050
- API: http://localhost:8001/health
- Frontend (dev): http://localhost:3001

---

## 📡 API Endpoints Reference

### Authentication
```
POST   /api/v1/auth/signup          - Create account
POST   /api/v1/auth/login           - Login (JWT)
GET    /api/v1/auth/me              - Get user profile
POST   /api/v1/auth/refresh         - Refresh token
```

### OAuth (NEW)
```
GET    /api/v1/auth/oauth/github    - GitHub login
GET    /api/v1/auth/oauth/google    - Google login
GET    /api/v1/auth/callback/github - GitHub callback
GET    /api/v1/auth/callback/google - Google callback
GET    /api/v1/auth/providers       - List enabled providers
```

### Repositories
```
POST   /api/v1/repositories         - Add repository
GET    /api/v1/repositories         - List repositories
GET    /api/v1/repositories/{id}    - Get repository
PUT    /api/v1/repositories/{id}    - Update repository
DELETE /api/v1/repositories/{id}    - Delete repository
```

### Scans
```
POST   /api/v1/scans                - Start scan
GET    /api/v1/scans                - List scans
GET    /api/v1/scans/{id}           - Get scan results
```

### Consent
```
POST   /api/v1/consent              - Record consent
GET    /api/v1/consent              - Get consents
DELETE /api/v1/consent/{id}         - Revoke consent
```

---

## 🗄️ Database

### Access Database
```bash
# Via Docker
docker exec -it forgetrace-platform-db psql -U forgetrace -d forgetrace_platform

# List tables
\dt

# View users
SELECT id, email, role, tenant_id FROM users;

# View scans
SELECT id, status, total_files, created_at FROM scans ORDER BY created_at DESC LIMIT 5;
```

### Tables (8 total)
- `tenants` - Multi-tenant organizations
- `users` - User accounts
- `repositories` - Connected repos
- `scans` - Scan executions
- `consent_records` - GDPR compliance
- `oauth_tokens` - OAuth credentials
- `audit_logs` - Immutable audit trail
- `alembic_version` - Migration tracking

---

## 🔍 Debugging

### View Logs
```bash
# Backend logs (if using nohup)
tail -f /tmp/forge-backend.log

# MLflow logs
docker logs forgetrace-mlflow
docker logs forgetrace-mlflow-db

# Database logs
docker logs forgetrace-platform-db
```

### Check Services
```bash
# Backend health
curl http://localhost:8001/health

# MLflow health  
curl http://localhost:5050/health

# Database connection
docker exec forgetrace-platform-db psql -U forgetrace -d forgetrace_platform -c "SELECT version();"

# Redis connection
docker exec forgetrace-platform-redis redis-cli ping
```

### Common Issues

**Backend not starting:**
```bash
# Check port availability
lsof -i :8001

# Kill existing process
pkill -f "uvicorn.*8001"

# Restart
cd forge_platform/backend
/home/papaert/projects/ForgeTrace/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**MLflow not accessible:**
```bash
# Check containers
docker ps | grep mlflow

# Restart
cd deployment/mlflow
docker-compose restart

# View logs
docker logs forgetrace-mlflow -f
```

**Database connection failed:**
```bash
# Check if running
docker ps | grep postgres

# Restart database
cd forge_platform/infra/docker
docker-compose restart postgres
```

---

## 📦 New Integrations (Steps 1-3)

### S3 Storage ✅
**Service:** `app.services.s3_storage`
- Automatic scan result uploads
- Presigned URL generation
- Artifact management
- Bucket creation scripts

**Usage:**
```python
from app.services.s3_storage import s3_storage

# Check if enabled
if s3_storage.is_enabled():
    # Upload results
    s3_url = await s3_storage.upload_scan_result(...)
```

### OAuth ✅
**Service:** `app.services.oauth`
- GitHub authentication
- Google authentication  
- Auto user/tenant creation
- Token management

**Test:**
```bash
# Check providers
curl http://localhost:8001/api/v1/auth/providers

# Login (browser)
open http://localhost:8001/api/v1/auth/oauth/github
```

### MLflow ✅
**Running:** http://localhost:5050
- Experiment tracking
- Model versioning
- Artifact storage (S3)
- PostgreSQL backend

**Usage:**
```python
import mlflow
mlflow.set_tracking_uri("http://localhost:5050")
```

---

## 🚀 Deploy to Production

### 1. Configure Secrets
```bash
# GitHub Actions secrets
gh secret set AWS_ACCESS_KEY_ID
gh secret set AWS_SECRET_ACCESS_KEY
gh secret set DATABASE_URL
gh secret set SECRET_KEY
gh secret set JWT_SECRET
gh secret set GITHUB_CLIENT_ID
gh secret set GITHUB_CLIENT_SECRET
gh secret set GOOGLE_CLIENT_ID
gh secret set GOOGLE_CLIENT_SECRET
```

### 2. Update OAuth Apps
- Add production callback URLs
- Update CORS origins
- Configure production domains

### 3. Deploy Services
```bash
# Push to trigger CI/CD
git push origin main

# Monitor deployment
kubectl rollout status deployment/forgetrace-backend -n production
kubectl rollout status deployment/forgetrace-frontend -n production
```

### 4. Verify Production
```bash
./forge_platform/verify_production.sh https://api.forgetrace.com https://app.forgetrace.com
```

---

## 📞 Support

**Documentation:**
- Main README: `forge_platform/README.md`
- Getting Started: `forge_platform/GETTING_STARTED.md`
- Deployment: `forge_platform/DEPLOYMENT_CHECKLIST.md`
- Integration Guide: `PRODUCTION_INTEGRATION_COMPLETE.md`

**API Documentation:**
- Interactive docs: http://localhost:8001/api/docs
- ReDoc: http://localhost:8001/api/redoc

---

**Last Updated:** November 23, 2025
**Platform Version:** 1.0.0
**Status:** ✅ All systems operational, production-ready
