# ForgeTrace Platform

Multi-tenant SaaS platform for IP audit and provenance analysis.

## Architecture

```
forge_platform/
├── backend/          # FastAPI backend with async SQLAlchemy
├── frontend/         # React + TypeScript + Tailwind CSS
└── infra/           
    ├── docker/       # Docker Compose for local development
    └── k8s/          # Kubernetes manifests for production
```

## Quick Start (Local Development)

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for frontend development)
- Python 3.12+ (for backend development)

### 1. Start Services

```bash
cd forge_platform/infra/docker
cp .env.example .env
# Edit .env with your configuration
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Backend API (port 8000)
- Frontend (port 3000)

### 2. Initialize Database

```bash
cd forge_platform/backend
pip install -r requirements.txt
alembic upgrade head
```

### 3. Access Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

## Development

### Backend Development

```bash
cd forge_platform/backend

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run migrations
alembic upgrade head

# Start dev server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd forge_platform/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### Database Migrations

```bash
cd forge_platform/backend

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Production Deployment

### Kubernetes Deployment

1. **Build and push images:**

```bash
# Backend
docker build -t ghcr.io/your-org/forgetrace-backend:latest \
  -f forge_platform/infra/docker/Dockerfile.backend \
  forge_platform/backend

docker push ghcr.io/your-org/forgetrace-backend:latest

# Frontend
docker build -t ghcr.io/your-org/forgetrace-frontend:latest \
  -f forge_platform/infra/docker/Dockerfile.frontend \
  forge_platform/frontend

docker push ghcr.io/your-org/forgetrace-frontend:latest
```

2. **Create secrets:**

```bash
kubectl create secret generic forgetrace-secrets \
  --from-literal=database-url='postgresql+asyncpg://...' \
  --from-literal=redis-url='redis://...' \
  --from-literal=secret-key='your-secret-key' \
  --from-literal=jwt-secret='your-jwt-secret'

kubectl create secret generic aws-credentials \
  --from-literal=access-key-id='YOUR_KEY' \
  --from-literal=secret-access-key='YOUR_SECRET'
```

3. **Deploy:**

```bash
cd forge_platform/infra/k8s

# Set environment variables
export REGISTRY=ghcr.io/your-org
export VERSION=latest

# Apply manifests
envsubst < backend-deployment.yaml | kubectl apply -f -
envsubst < frontend-deployment.yaml | kubectl apply -f -
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml
```

## API Documentation

Once running, visit:
- Development: http://localhost:8000/api/docs
- Production: https://api.forgetrace.com/docs

## Key Features

### Backend
- ✅ Multi-tenant architecture with row-level security
- ✅ JWT authentication with refresh tokens
- ✅ OAuth integration (GitHub, Google)
- ✅ Async SQLAlchemy with PostgreSQL
- ✅ Redis caching
- ✅ Consent management system (GDPR/CCPA compliant)
- ✅ Audit logging
- ✅ S3 integration for scan artifacts
- ✅ MLflow integration for model tracking

### Frontend
- ✅ React 18 with TypeScript
- ✅ Tailwind CSS for styling
- ✅ React Router for navigation
- ✅ Zustand for state management
- ✅ React Query for API calls
- ✅ Responsive design

## Configuration

### Environment Variables

See `.env.example` files in backend and frontend directories.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: Application secret key
- `JWT_SECRET`: JWT signing secret
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`: AWS credentials
- `MLFLOW_TRACKING_URI`: MLflow server URL

## Testing

### Backend Tests
```bash
cd forge_platform/backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd forge_platform/frontend
npm test
```

## CI/CD

GitHub Actions workflow (`.github/workflows/platform-ci.yml`) handles:
- Running tests
- Building Docker images
- Pushing to GitHub Container Registry
- Deploying to staging/production Kubernetes clusters

## Monitoring

- Health check: `/health`
- Metrics: Prometheus metrics exposed on `/metrics` (add middleware)
- Logs: Structured JSON logging to stdout

## Security

- HTTPS enforced in production
- CORS configured
- Rate limiting
- SQL injection protection (SQLAlchemy)
- XSS protection
- CSRF protection
- Secure password hashing (bcrypt)
- JWT token expiration
- Multi-tenancy isolation

## Support

- Documentation: `/docs`
- Issues: GitHub Issues
- Email: support@forgetrace.com

## License

Proprietary - All Rights Reserved
© 2025 BAMG Studio LLC
