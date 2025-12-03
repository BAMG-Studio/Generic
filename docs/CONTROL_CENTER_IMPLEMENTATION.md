# ForgeTrace Control Center Implementation Guide

## Quick Start

This guide walks you through implementing the ForgeTrace Control Center with multi-domain architecture and role-based access control.

## Prerequisites

- Domain names configured:
  - `www.forgetrace.pro` (public site)
  - `app.forgetrace.pro` (control center)
  - `api.forgetrace.pro` (backend API)
- SSL certificates (AWS Certificate Manager or Let's Encrypt)
- AWS account (for infrastructure)
- PostgreSQL database
- Redis instance

## Phase 1: Infrastructure Setup

### 1.1 Domain Configuration

```bash
# Configure DNS records (Route 53 or your DNS provider)
www.forgetrace.pro    A/CNAME  → CloudFront distribution
app.forgetrace.pro    A/CNAME  → CloudFront distribution  
api.forgetrace.pro    A/CNAME  → Application Load Balancer
```

### 1.2 SSL Certificates

```bash
# Request certificates in AWS Certificate Manager
# - *.forgetrace.pro (wildcard)
# - forgetrace.pro (apex)

# Or use Let's Encrypt
certbot certonly --dns-route53 -d "*.forgetrace.pro" -d "forgetrace.pro"
```

### 1.3 Database Setup

```sql
-- Create database
CREATE DATABASE forgetrace_platform;

-- Run migrations
cd forge_platform/backend
alembic upgrade head
```

### 1.4 Redis Setup

```bash
# Using Docker
docker run -d --name forgetrace-redis \
  -p 6379:6379 \
  redis:7-alpine

# Or AWS ElastiCache
# Create Redis cluster in AWS Console
```

## Phase 2: Backend API Deployment

### 2.1 Environment Configuration

```bash
cd forge_platform/backend
cp .env.example .env
```

Edit `.env`:

```env
# Application
ENV=production
DEBUG=false
API_PREFIX=/api/v1

# Security
SECRET_KEY=<generate-strong-random-key>
JWT_SECRET=<generate-strong-random-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/forgetrace_platform

# Redis
REDIS_URL=redis://host:6379/0

# OAuth
GITHUB_CLIENT_ID=<your-github-client-id>
GITHUB_CLIENT_SECRET=<your-github-client-secret>
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
OAUTH_CALLBACK_URL=https://api.forgetrace.pro/api/v1/auth/callback

# AWS
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
S3_BUCKET_SCANS=forgetrace-scans
S3_BUCKET_MODELS=forgetrace-models

# CORS
CORS_ORIGINS=["https://app.forgetrace.pro","https://www.forgetrace.pro"]
```

### 2.2 Deploy Backend

Using Docker:

```bash
cd forge_platform/infra/docker

# Build image
docker build -f Dockerfile.backend -t forgetrace-api:latest ../../backend

# Run container
docker run -d \
  --name forgetrace-api \
  -p 8000:8000 \
  --env-file ../../backend/.env \
  forgetrace-api:latest
```

Using Kubernetes:

```bash
cd forge_platform/infra/k8s

# Update secrets
kubectl create secret generic forgetrace-secrets \
  --from-env-file=../../backend/.env

# Deploy
kubectl apply -f backend-deployment.yaml
kubectl apply -f ingress.yaml
```

### 2.3 Verify API

```bash
curl https://api.forgetrace.pro/health
# Expected: {"status": "healthy"}

curl https://api.forgetrace.pro/api/v1/health
# Expected: {"status": "ok", "version": "1.0.0"}
```

## Phase 3: Frontend Deployment

### 3.1 Build Frontend

```bash
cd forge_platform/frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
```

Edit `.env`:

```env
VITE_API_URL=https://api.forgetrace.pro
VITE_APP_NAME=ForgeTrace
VITE_ENABLE_OAUTH=true
```

Build:

```bash
npm run build
# Output: dist/
```

### 3.2 Deploy to S3 + CloudFront

```bash
# Upload to S3
aws s3 sync dist/ s3://app-forgetrace-pro/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id <your-distribution-id> \
  --paths "/*"
```

### 3.3 Verify Frontend

Visit `https://app.forgetrace.pro` - you should see the login gateway.

## Phase 4: Public Website

### 4.1 Create Marketing Site

```bash
# Create simple Next.js site or static HTML
mkdir public-site
cd public-site

# Example structure:
# index.html - Landing page
# /docs - Documentation
# /pricing - Pricing page
# /download - App download links
```

### 4.2 Deploy Public Site

```bash
# Upload to S3
aws s3 sync . s3://www-forgetrace-pro/ --delete

# Invalidate CloudFront
aws cloudfront create-invalidation \
  --distribution-id <your-distribution-id> \
  --paths "/*"
```

## Phase 5: Initial Setup

### 5.1 Create Super Admin User

```bash
# Connect to database
psql $DATABASE_URL

# Create super admin
INSERT INTO users (id, email, hashed_password, full_name, role, is_active, is_verified, tenant_id, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  'admin@forgetrace.pro',
  '<bcrypt-hashed-password>',
  'System Administrator',
  'super_admin',
  true,
  true,
  gen_random_uuid(),
  NOW(),
  NOW()
);
```

Or use the API:

```bash
curl -X POST https://api.forgetrace.pro/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@forgetrace.pro",
    "password": "SecurePassword123!",
    "full_name": "System Administrator"
  }'
```

### 5.2 Create First Tenant

```bash
curl -X POST https://api.forgetrace.pro/api/v1/tenants \
  -H "Authorization: Bearer <admin-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation",
    "slug": "acme-corp",
    "tier": "professional"
  }'
```

### 5.3 Generate API Token

```bash
curl -X POST https://api.forgetrace.pro/api/v1/tokens \
  -H "Authorization: Bearer <user-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production API Token",
    "scopes": "read:audits,write:audits,read:reports",
    "expires_at": null
  }'

# Response includes the token (only shown once):
# {
#   "token": "ftk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
#   "prefix": "ftk_xxxxxxxx",
#   "id": "uuid",
#   "scopes": "read:audits,write:audits,read:reports"
# }
```

## Phase 6: Testing Authentication

### 6.1 Test Client Token Auth

```bash
# Verify token
curl https://api.forgetrace.pro/api/v1/auth/verify-token \
  -H "Authorization: Bearer ftk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Submit audit with token
curl -X POST https://api.forgetrace.pro/api/v1/audits \
  -H "Authorization: Bearer ftk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "https://github.com/user/repo",
    "branch": "main"
  }'
```

### 6.2 Test Management Credentials Auth

```bash
# Login
curl -X POST https://api.forgetrace.pro/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@forgetrace.pro",
    "password": "SecurePassword123!"
  }'

# Response:
# {
#   "access_token": "eyJ...",
#   "refresh_token": "eyJ...",
#   "user": {...}
# }

# Use JWT for management operations
curl https://api.forgetrace.pro/api/v1/users \
  -H "Authorization: Bearer eyJ..."
```

### 6.3 Test OAuth Flow

1. Visit `https://app.forgetrace.pro`
2. Click "Management Sign In"
3. Click "GitHub" or "Google"
4. Authorize the application
5. Should redirect back to dashboard

## Phase 7: Mobile App Integration

### 7.1 Configure Deep Links

iOS (`Info.plist`):

```xml
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>forgetrace</string>
    </array>
  </dict>
</array>
```

Android (`AndroidManifest.xml`):

```xml
<intent-filter>
  <action android:name="android.intent.action.VIEW" />
  <category android:name="android.intent.category.DEFAULT" />
  <category android:name="android.intent.category.BROWSABLE" />
  <data android:scheme="forgetrace" />
</intent-filter>
```

### 7.2 Mobile Authentication Flow

```typescript
// React Native example
import AsyncStorage from '@react-native-async-storage/async-storage';

// Token authentication
async function loginWithToken(token: string) {
  const response = await fetch('https://api.forgetrace.pro/api/v1/auth/verify-token', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  if (response.ok) {
    const data = await response.json();
    await AsyncStorage.setItem('auth_token', token);
    await AsyncStorage.setItem('user', JSON.stringify(data.user));
  }
}

// Credential authentication
async function loginWithCredentials(email: string, password: string) {
  const response = await fetch('https://api.forgetrace.pro/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  
  if (response.ok) {
    const data = await response.json();
    await AsyncStorage.setItem('auth_token', data.access_token);
    await AsyncStorage.setItem('refresh_token', data.refresh_token);
    await AsyncStorage.setItem('user', JSON.stringify(data.user));
  }
}
```

## Phase 8: Monitoring & Maintenance

### 8.1 Set Up Monitoring

```bash
# CloudWatch alarms
aws cloudwatch put-metric-alarm \
  --alarm-name forgetrace-api-errors \
  --alarm-description "Alert on high error rate" \
  --metric-name 5XXError \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold

# Application metrics
# Add to backend/app/main.py:
from prometheus_client import Counter, Histogram

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
```

### 8.2 Log Aggregation

```python
# backend/app/core/logging.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
        }
        return json.dumps(log_data)

# Configure in main.py
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)
logging.getLogger().handlers[0].setFormatter(JSONFormatter())
```

### 8.3 Backup Strategy

```bash
# Database backups
pg_dump $DATABASE_URL | gzip > backup-$(date +%Y%m%d).sql.gz

# Upload to S3
aws s3 cp backup-$(date +%Y%m%d).sql.gz s3://forgetrace-backups/

# Automated daily backups (cron)
0 2 * * * /path/to/backup-script.sh
```

## Troubleshooting

### Issue: CORS errors

**Solution**: Verify CORS_ORIGINS in backend `.env` includes your frontend domain.

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Token authentication fails

**Solution**: Check token format and database entry.

```bash
# Verify token in database
psql $DATABASE_URL -c "SELECT token_prefix, is_active, expires_at FROM api_tokens WHERE token_prefix = 'ftk_xxxxxxxx';"

# Check token hash
python -c "import hashlib; print(hashlib.sha256(b'ftk_your_token_here').hexdigest())"
```

### Issue: OAuth redirect fails

**Solution**: Verify callback URL matches OAuth provider settings.

```bash
# GitHub: https://github.com/settings/developers
# Callback URL: https://api.forgetrace.pro/api/v1/auth/callback

# Google: https://console.cloud.google.com/apis/credentials
# Authorized redirect URI: https://api.forgetrace.pro/api/v1/auth/callback
```

## Security Checklist

- [ ] SSL/TLS enabled on all domains
- [ ] Strong JWT secrets (32+ characters)
- [ ] API tokens hashed with SHA-256
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Database credentials secured
- [ ] OAuth secrets in environment variables
- [ ] Regular security updates
- [ ] Audit logging enabled
- [ ] Backup strategy in place

## Performance Optimization

### Caching Strategy

```python
# backend/app/middleware/cache.py
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(settings.REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="forgetrace-cache")

# Use in endpoints
from fastapi_cache.decorator import cache

@router.get("/audits/{id}")
@cache(expire=300)  # 5 minutes
async def get_audit(id: str):
    ...
```

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_audits_tenant_created ON audits(tenant_id, created_at DESC);
CREATE INDEX idx_tokens_user_active ON api_tokens(user_id, is_active);
CREATE INDEX idx_usage_user_period ON usage_aggregates(user_id, period_date);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM audits WHERE tenant_id = 'xxx' ORDER BY created_at DESC LIMIT 10;
```

## Next Steps

1. **Set up CI/CD pipeline** - Automate deployments
2. **Implement webhooks** - Real-time notifications
3. **Add analytics dashboard** - Usage insights
4. **Build mobile apps** - iOS and Android
5. **Create admin panel** - System management
6. **Add billing integration** - Stripe/payment processing
7. **Implement SSO** - Enterprise authentication
8. **Add audit logs** - Compliance tracking

## Support

- Documentation: https://www.forgetrace.pro/docs
- Email: hello@bamgstudio.com
- GitHub Issues: https://github.com/BAMG-Studio/ForgeTrace/issues
