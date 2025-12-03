# ForgeTrace Control Center

**Multi-domain, role-based access control platform for IP audit services**

## Overview

The ForgeTrace Control Center is a comprehensive platform that provides:

- **Multi-domain architecture** - Separate domains for public site, app, and API
- **Dual authentication** - Token-based for clients, credential-based for management
- **Role-based access control** - Granular permissions for different user types
- **Subscription tiers** - Free, Professional, and Enterprise with different capabilities
- **Mobile app support** - iOS and Android with seamless authentication

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  www.forgetrace.pro                          │
│                 (Public Marketing Site)                      │
│  • Product info  • Documentation  • App downloads           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  app.forgetrace.pro                          │
│                 (Control Center Dashboard)                   │
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  Client Portal   │         │ Management Portal│         │
│  │  (Token Auth)    │         │ (Credentials)    │         │
│  └──────────────────┘         └──────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  api.forgetrace.pro                          │
│                     (Backend API)                            │
│  • Authentication  • Audits  • Reports  • Tokens            │
└─────────────────────────────────────────────────────────────┘
```

## User Types

### Client Users (Token-Based)
- Purchase subscription → receive API token
- Access via token authentication
- Limited to specific scopes based on tier
- View reports and usage statistics

### Management Users (Credential-Based)
- Email/password or OAuth (GitHub/Google)
- Full dashboard access
- Role-based permissions (Super Admin, Tenant Admin, User, Viewer)
- Manage users, tokens, and settings

## Subscription Tiers

### Free Tier
- 1,000 files/month
- 60 requests/minute
- Basic audit reports
- Scopes: `read:reports`, `read:audits`

### Professional Tier
- 50,000 files/month
- 300 requests/minute
- Full audit suite
- Priority queue
- Webhook integrations
- Scopes: `read:*`, `write:audits`, `write:webhooks`

### Enterprise Tier
- Custom quotas
- Dedicated resources
- Custom SLA
- White-label options
- All scopes including `admin:*`

## Quick Start

### 1. Set Up Infrastructure

```bash
# Clone repository
git clone https://github.com/BAMG-Studio/ForgeTrace.git
cd ForgeTrace/forge_platform

# Set up environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit configuration files with your settings
```

### 2. Deploy Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Deploy Frontend

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Serve (or deploy to S3/CloudFront)
npm run preview
```

### 4. Create First User

```bash
# Register super admin
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@forgetrace.pro",
    "password": "SecurePassword123!",
    "full_name": "System Administrator"
  }'
```

## Authentication Flows

### Client Token Authentication

```bash
# 1. Purchase subscription (via website)
# 2. Receive API token: ftk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 3. Use token for API requests
curl https://api.forgetrace.pro/api/v1/audits \
  -H "Authorization: Bearer ftk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 4. Access client portal
# Visit app.forgetrace.pro → Client Sign In → Enter token
```

### Management Credential Authentication

```bash
# 1. Login with email/password
curl -X POST https://api.forgetrace.pro/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@forgetrace.pro",
    "password": "SecurePassword123!"
  }'

# Response includes JWT tokens
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {...}
}

# 2. Use JWT for subsequent requests
curl https://api.forgetrace.pro/api/v1/users \
  -H "Authorization: Bearer eyJ..."
```

### OAuth Authentication

```bash
# 1. Visit app.forgetrace.pro
# 2. Click "Management Sign In"
# 3. Click "GitHub" or "Google"
# 4. Authorize application
# 5. Redirected to dashboard with JWT tokens
```

## API Endpoints

### Authentication
```
POST   /api/v1/auth/register          - Register new user
POST   /api/v1/auth/login             - Login with credentials
POST   /api/v1/auth/refresh           - Refresh JWT token
POST   /api/v1/auth/logout            - Logout
GET    /api/v1/auth/me                - Get current user
POST   /api/v1/auth/verify-token      - Verify API token
```

### Audits
```
POST   /api/v1/audits                 - Submit new audit
GET    /api/v1/audits                 - List audits
GET    /api/v1/audits/{id}            - Get audit details
GET    /api/v1/audits/{id}/report     - Download report
DELETE /api/v1/audits/{id}            - Delete audit
```

### Tokens (Management Only)
```
POST   /api/v1/tokens                 - Create API token
GET    /api/v1/tokens                 - List tokens
GET    /api/v1/tokens/{id}            - Get token details
PATCH  /api/v1/tokens/{id}            - Update token
DELETE /api/v1/tokens/{id}            - Revoke token
```

### Users (Admin Only)
```
GET    /api/v1/users                  - List users
POST   /api/v1/users                  - Create user
GET    /api/v1/users/{id}             - Get user
PATCH  /api/v1/users/{id}             - Update user
DELETE /api/v1/users/{id}             - Delete user
```

## Role-Based Permissions

### Super Admin
- Full system access
- Manage all tenants
- View all audits
- Configure platform settings
- Access analytics and billing

### Tenant Admin
- Manage organization users
- View organization audits
- Manage API tokens
- Configure organization settings
- Access organization billing

### User
- Submit audits
- View own audits
- Create personal API tokens
- Access assigned projects

### Viewer
- View assigned audits
- Download reports

## Token Scopes

### Available Scopes
```
read:audits          - Read audit data
write:audits         - Submit new audits
delete:audits        - Delete audits
read:reports         - Read reports
generate:reports     - Generate new reports
export:reports       - Export reports
read:webhooks        - Read webhook configs
write:webhooks       - Configure webhooks
admin:tenant         - Tenant administration
```

### Wildcard Scopes
```
read:*               - All read permissions
write:*              - All write permissions
admin:*              - All admin permissions
```

## Mobile App Integration

### iOS Setup

```swift
// AppDelegate.swift
func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey : Any] = [:]) -> Bool {
    if url.scheme == "forgetrace" {
        // Handle deep link
        handleAuthCallback(url: url)
        return true
    }
    return false
}
```

### Android Setup

```kotlin
// MainActivity.kt
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    
    intent?.data?.let { uri ->
        if (uri.scheme == "forgetrace") {
            handleAuthCallback(uri)
        }
    }
}
```

### Authentication

```typescript
// Token authentication
async function loginWithToken(token: string) {
  const response = await fetch('https://api.forgetrace.pro/api/v1/auth/verify-token', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
  });
  
  if (response.ok) {
    const data = await response.json();
    await SecureStore.setItemAsync('auth_token', token);
    return data.user;
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
    await SecureStore.setItemAsync('access_token', data.access_token);
    await SecureStore.setItemAsync('refresh_token', data.refresh_token);
    return data.user;
  }
}
```

## Deployment

### Using Docker Compose

```bash
cd forge_platform/infra/docker
docker-compose up -d
```

### Using Kubernetes

```bash
cd forge_platform/infra/k8s

# Create secrets
kubectl create secret generic forgetrace-secrets \
  --from-env-file=../../backend/.env

# Deploy
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f ingress.yaml
```

### Using AWS

See [CONTROL_CENTER_IMPLEMENTATION.md](../../docs/CONTROL_CENTER_IMPLEMENTATION.md) for detailed AWS deployment guide.

## Monitoring

### Health Checks

```bash
# API health
curl https://api.forgetrace.pro/health

# Database connectivity
curl https://api.forgetrace.pro/api/v1/health

# Redis connectivity
curl https://api.forgetrace.pro/api/v1/health/redis
```

### Metrics

```bash
# Prometheus metrics
curl https://api.forgetrace.pro/metrics

# Key metrics:
# - http_requests_total
# - http_request_duration_seconds
# - active_users
# - api_tokens_active
# - audits_processing
```

### Logs

```bash
# View backend logs
docker logs forgetrace-api -f

# View frontend logs
docker logs forgetrace-frontend -f

# CloudWatch logs (AWS)
aws logs tail /aws/ecs/forgetrace-api --follow
```

## Security

### Best Practices

1. **Use strong secrets** - Generate random 32+ character keys
2. **Enable HTTPS** - Use SSL/TLS for all domains
3. **Rotate tokens** - Regularly rotate API tokens and JWT secrets
4. **Rate limiting** - Enforce rate limits per tier
5. **Audit logging** - Log all authentication and authorization events
6. **Regular updates** - Keep dependencies up to date
7. **Backup strategy** - Regular database and S3 backups

### Security Headers

```python
# backend/app/main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.forgetrace.pro"])
app.add_middleware(HTTPSRedirectMiddleware)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

## Troubleshooting

### Common Issues

**CORS errors**
- Verify CORS_ORIGINS in backend .env
- Check browser console for specific error

**Token authentication fails**
- Verify token format (starts with ftk_)
- Check token is active in database
- Verify token hasn't expired

**OAuth redirect fails**
- Check callback URL matches provider settings
- Verify OAuth credentials in .env

**Database connection fails**
- Check DATABASE_URL format
- Verify database is running
- Check network connectivity

## Support

- **Documentation**: https://www.forgetrace.pro/docs
- **Email**: hello@bamgstudio.com
- **GitHub**: https://github.com/BAMG-Studio/ForgeTrace
- **Issues**: https://github.com/BAMG-Studio/ForgeTrace/issues

## License

Proprietary - All Rights Reserved

Built by Peter Kolawole, BAMG Studio LLC
