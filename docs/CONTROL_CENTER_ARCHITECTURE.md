# ForgeTrace Control Center Architecture

## Overview

ForgeTrace Control Center is a comprehensive multi-domain platform that provides role-based access control for IP audit services. The system consists of three primary domains with distinct responsibilities.

## Domain Structure

### 1. **www.forgetrace.pro** - Public Marketing Site
- **Purpose**: Public-facing website for marketing, documentation, and app downloads
- **Features**:
  - Product information and pricing
  - Documentation and guides
  - Mobile app download links (iOS/Android)
  - Blog and resources
  - Contact and support
- **Tech Stack**: Static site (Next.js/React) + CDN
- **Authentication**: None (public)

### 2. **app.forgetrace.pro** - Control Center Dashboard
- **Purpose**: Main application interface for authenticated users
- **Features**:
  - Mission Control dashboard
  - Code DNA explorer
  - Review queue
  - Developer portal (API tokens)
  - Settings and preferences
  - Audit history and reports
- **Tech Stack**: React + TypeScript + Vite
- **Authentication**: JWT-based with role-based access control

### 3. **api.forgetrace.pro** - Backend API
- **Purpose**: RESTful API for all platform operations
- **Features**:
  - Authentication endpoints
  - Audit submission and retrieval
  - Token management
  - User and tenant management
  - Webhook integrations
- **Tech Stack**: FastAPI + PostgreSQL + Redis
- **Authentication**: JWT tokens + API tokens

## Authentication & Authorization Architecture

### User Types

#### 1. **Client Users** (Token-Based Access)
- Authenticate via API tokens purchased through subscription
- Access level determined by token tier
- No password required (token-only authentication)
- Limited to specific scopes based on subscription

#### 2. **Management Users** (Credential-Based Access)
- Authenticate via email/password or OAuth
- Full dashboard access with role-based permissions
- Can manage tenants, users, and system settings

### Role Hierarchy

```
SUPER_ADMIN (Platform Owner)
├── Full system access
├── Manage all tenants
├── View all audits and reports
├── Configure platform settings
└── Access to analytics and billing

TENANT_ADMIN (Organization Admin)
├── Manage organization users
├── View organization audits
├── Manage API tokens
├── Configure organization settings
└── Access to organization billing

USER (Standard User)
├── Submit audits
├── View own audits
├── Create personal API tokens
└── Access to assigned projects

VIEWER (Read-Only)
├── View assigned audits
└── Download reports
```

### Token Tiers & Permissions

#### Free Tier
- **Limits**: 1,000 files/month, 60 requests/minute
- **Scopes**: `read:reports`, `read:audits`
- **Features**: Basic audit reports, limited history

#### Professional Tier
- **Limits**: 50,000 files/month, 300 requests/minute
- **Scopes**: `read:*`, `write:audits`, `write:webhooks`
- **Features**: Full audit suite, priority queue, webhook integrations

#### Enterprise Tier
- **Limits**: Custom quotas, dedicated resources
- **Scopes**: All scopes + `admin:*`
- **Features**: Custom SLA, dedicated support, white-label options

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    www.forgetrace.pro                        │
│                   (Public Marketing Site)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Landing    │  │     Docs     │  │  App Store   │      │
│  │     Page     │  │   & Guides   │  │    Links     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   app.forgetrace.pro                         │
│                  (Control Center Dashboard)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Login Gateway                      │   │
│  │  ┌────────────────┐         ┌────────────────┐      │   │
│  │  │ Client Sign In │         │ Management     │      │   │
│  │  │ (Token Auth)   │         │ Sign In        │      │   │
│  │  │                │         │ (Credentials)  │      │   │
│  │  └────────────────┘         └────────────────┘      │   │
│  └──────────────────────────────────────────────────────┘   │
│                              │                               │
│              ┌───────────────┴───────────────┐              │
│              ▼                               ▼              │
│  ┌─────────────────────┐         ┌─────────────────────┐   │
│  │   Client Portal     │         │  Management Portal  │   │
│  │                     │         │                     │   │
│  │ • View Reports      │         │ • Full Dashboard    │   │
│  │ • Download Audits   │         │ • User Management   │   │
│  │ • API Usage Stats   │         │ • Token Management  │   │
│  │ • Subscription Info │         │ • Analytics         │   │
│  └─────────────────────┘         │ • System Settings   │   │
│                                   └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   api.forgetrace.pro                         │
│                      (Backend API)                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Authentication Layer                     │   │
│  │  • JWT Validation                                     │   │
│  │  • API Token Validation                               │   │
│  │  • Role-Based Access Control                          │   │
│  │  • Rate Limiting                                      │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  API Endpoints                        │   │
│  │  /auth/*        - Authentication                      │   │
│  │  /audits/*      - Audit operations                    │   │
│  │  /tokens/*      - Token management                    │   │
│  │  /users/*       - User management                     │   │
│  │  /tenants/*     - Tenant management                   │   │
│  │  /reports/*     - Report generation                   │   │
│  │  /webhooks/*    - Webhook configuration               │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  Data Layer                           │   │
│  │  • PostgreSQL (Users, Tenants, Audits)               │   │
│  │  • Redis (Sessions, Cache, Rate Limits)              │   │
│  │  • S3 (Audit Reports, Artifacts)                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Authentication Flow

### Client Token Authentication
```
1. Client purchases subscription → receives API token
2. Client makes API request with token in header:
   Authorization: Bearer ftk_xxxxxxxxxxxxx
3. API validates token:
   - Check token exists and is active
   - Verify not expired
   - Check rate limits for tier
   - Validate scopes for endpoint
4. Request processed with client context
```

### Management Credential Authentication
```
1. User visits app.forgetrace.pro
2. Clicks "Management Sign In"
3. Enters email/password or uses OAuth (GitHub/Google)
4. Backend validates credentials
5. Issues JWT access token + refresh token
6. Frontend stores tokens securely
7. Subsequent requests include JWT in Authorization header
8. Backend validates JWT and role permissions
```

## Database Schema

### Core Tables

#### users
- id (UUID, PK)
- email (unique)
- hashed_password (nullable for OAuth)
- full_name
- role (enum: super_admin, tenant_admin, user, viewer)
- tenant_id (FK)
- is_active, is_verified
- oauth_provider, oauth_id
- created_at, updated_at

#### tenants
- id (UUID, PK)
- name, slug (unique)
- tier (enum: free, professional, enterprise)
- max_repos, max_scans_per_month, max_users
- stripe_customer_id
- subscription_status
- is_active
- created_at, updated_at

#### api_tokens
- id (UUID, PK)
- user_id (FK)
- tenant_id (FK)
- name (user-friendly label)
- token_prefix (for display: ftk_xxxxxxxx)
- hashed_token (SHA-256)
- scopes (comma-separated)
- tier (enum: free, professional, enterprise)
- expires_at (nullable)
- last_used_at
- is_active
- created_at, updated_at

#### audits
- id (UUID, PK)
- tenant_id (FK)
- user_id (FK)
- repository_url
- branch
- status (enum: pending, processing, completed, failed)
- result_s3_key
- files_scanned
- created_at, completed_at

#### token_usage_events
- id (UUID, PK)
- token_id (FK)
- user_id (FK)
- endpoint, method, status_code
- files_scanned
- ip_address, user_agent
- created_at

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

### OAuth
```
GET    /api/v1/oauth/{provider}       - Initiate OAuth flow
GET    /api/v1/oauth/callback         - OAuth callback
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
GET    /api/v1/tokens/{id}/usage      - Get usage stats
```

### Users (Admin Only)
```
GET    /api/v1/users                  - List users
POST   /api/v1/users                  - Create user
GET    /api/v1/users/{id}             - Get user
PATCH  /api/v1/users/{id}             - Update user
DELETE /api/v1/users/{id}             - Delete user
```

### Tenants (Super Admin Only)
```
GET    /api/v1/tenants                - List tenants
POST   /api/v1/tenants                - Create tenant
GET    /api/v1/tenants/{id}           - Get tenant
PATCH  /api/v1/tenants/{id}           - Update tenant
DELETE /api/v1/tenants/{id}           - Delete tenant
```

## Security Considerations

1. **Token Security**
   - API tokens hashed with SHA-256
   - Tokens prefixed with `ftk_` for identification
   - Rate limiting per token tier
   - Automatic revocation on suspicious activity

2. **JWT Security**
   - Short-lived access tokens (60 minutes)
   - Refresh tokens with rotation
   - Secure HTTP-only cookies for web
   - Token blacklisting on logout

3. **Data Isolation**
   - Tenant-level data isolation
   - Row-level security in database
   - S3 bucket policies per tenant
   - Audit logs for all operations

4. **Rate Limiting**
   - Per-token rate limits based on tier
   - Per-IP rate limits for auth endpoints
   - Distributed rate limiting via Redis
   - Graceful degradation under load

## Deployment Architecture

### Infrastructure
- **Load Balancer**: AWS ALB/CloudFront
- **API Servers**: ECS Fargate or EKS
- **Database**: RDS PostgreSQL (Multi-AZ)
- **Cache**: ElastiCache Redis (Cluster mode)
- **Storage**: S3 with lifecycle policies
- **CDN**: CloudFront for static assets

### Domain Configuration
```
www.forgetrace.pro    → CloudFront → S3 (static site)
app.forgetrace.pro    → CloudFront → S3 (React SPA)
api.forgetrace.pro    → ALB → ECS/EKS (FastAPI)
```

### SSL/TLS
- AWS Certificate Manager for SSL certificates
- Automatic certificate renewal
- TLS 1.3 minimum
- HSTS headers enabled

## Mobile App Integration

### App Download Flow
1. User visits www.forgetrace.pro
2. Clicks "Download App" (iOS/Android)
3. Redirected to App Store/Play Store
4. Installs ForgeTrace mobile app

### Mobile Authentication
1. App opens to login screen
2. User selects authentication method:
   - **Client**: Enter API token
   - **Management**: Email/password or OAuth
3. App stores credentials securely (Keychain/Keystore)
4. Subsequent API calls include authentication

### Mobile Features
- View audit reports
- Submit new audits
- Receive push notifications
- Offline report viewing
- Biometric authentication

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1-2)
- [ ] Set up domain routing
- [ ] Configure SSL certificates
- [ ] Deploy static marketing site
- [ ] Set up database and Redis

### Phase 2: Authentication System (Week 2-3)
- [ ] Implement JWT authentication
- [ ] Implement API token system
- [ ] Add OAuth providers
- [ ] Build login gateway UI

### Phase 3: RBAC & Permissions (Week 3-4)
- [ ] Implement role-based middleware
- [ ] Add permission checks to endpoints
- [ ] Build admin user management
- [ ] Create token management UI

### Phase 4: Client Portal (Week 4-5)
- [ ] Build client dashboard
- [ ] Add usage statistics
- [ ] Implement report viewer
- [ ] Add subscription management

### Phase 5: Management Portal (Week 5-6)
- [ ] Build full dashboard
- [ ] Add analytics and monitoring
- [ ] Implement tenant management
- [ ] Add system settings

### Phase 6: Mobile App (Week 7-8)
- [ ] Develop iOS app
- [ ] Develop Android app
- [ ] Implement mobile authentication
- [ ] Add push notifications

## Monitoring & Analytics

### Metrics to Track
- API request volume and latency
- Token usage by tier
- Audit processing times
- Error rates and types
- User engagement metrics
- Subscription conversions

### Logging
- Structured JSON logs
- Centralized logging (CloudWatch/ELK)
- Audit trail for all operations
- Security event logging

### Alerting
- High error rates
- Unusual token usage patterns
- System resource exhaustion
- Failed authentication attempts
- Payment failures

## Cost Optimization

1. **Compute**: Auto-scaling based on demand
2. **Storage**: S3 lifecycle policies for old reports
3. **Database**: Read replicas for analytics
4. **CDN**: Cache static assets aggressively
5. **Monitoring**: Sample high-volume metrics

## Next Steps

1. Review and approve architecture
2. Set up development environment
3. Begin Phase 1 implementation
4. Create detailed API specifications
5. Design UI/UX mockups
6. Set up CI/CD pipelines
