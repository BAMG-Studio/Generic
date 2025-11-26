# Getting Started with ForgeTrace Platform

This guide will help you get the ForgeTrace platform running locally in under 10 minutes.

## Prerequisites

Before starting, ensure you have:

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Python** 3.12+ (for backend development)
- **Node.js** 20+ (for frontend development)
- **Git**

## Step-by-Step Setup

### 1. Run Quick Setup Script

From the project root:

```bash
chmod +x forge_platform/setup.sh
./forge_platform/setup.sh
```

This will create necessary `.env` files with default values.

### 2. Review Configuration

Edit the generated `.env` files as needed:

```bash
# Backend configuration
nano forge_platform/backend/.env

# Docker environment
nano forge_platform/infra/docker/.env
```

**Important settings to review:**
- Database password
- JWT secrets (auto-generated)
- AWS credentials (if using S3)
- MLflow settings (if using model tracking)

### 3. Start Docker Services

```bash
cd forge_platform/infra/docker
docker-compose up -d
```

This starts:
- PostgreSQL database
- Redis cache
- Backend API server
- Frontend web server

### 4. Initialize Database

```bash
cd ../../backend
pip install -r requirements.txt
alembic upgrade head
```

### 5. Verify Installation

Check that all services are running:

```bash
docker-compose ps
```

You should see 4 services running:
- `postgres`
- `redis`
- `backend`
- `frontend`

### 6. Access the Platform

Open your browser:

- **Frontend**: <http://localhost:3000>
- **API Documentation**: <http://localhost:8000/api/docs>
- **API Health Check**: <http://localhost:8000/health>

## First Steps

### Create Your First Account

1. Navigate to <http://localhost:3000/signup>
2. Fill in the signup form:
   - Email
   - Password
   - Company name (becomes your tenant name)
3. Click "Sign Up"

### Connect a Repository

1. Log in with your new account
2. On the dashboard, click "Add Repository"
3. Enter repository details:
   - Name
   - URL (GitHub, GitLab, etc.)
   - Optional: Access token
4. Click "Connect Repository"

### Run Your First Scan

1. Select a connected repository
2. Click "Start Scan"
3. Monitor scan progress in the dashboard
4. View results when complete

## Development Workflow

### Backend Development

```bash
cd forge_platform/backend

# Install dependencies
pip install -r requirements.txt

# Run dev server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd forge_platform/frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

The frontend will be available at <http://localhost:5173> (Vite dev server).

### Database Changes

When you modify models:

```bash
cd forge_platform/backend

# Create migration
alembic revision --autogenerate -m "Description of change"

# Review migration in alembic/versions/

# Apply migration
alembic upgrade head
```

## Troubleshooting

### Services Won't Start

Check Docker logs:

```bash
cd forge_platform/infra/docker
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

### Database Connection Error

Ensure PostgreSQL is running:

```bash
docker-compose ps postgres
```

Check credentials in `.env` files match.

### Frontend Can't Reach Backend

Verify backend is running:

```bash
curl http://localhost:8000/health
```

Check CORS settings in `backend/.env`:

```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Port Already in Use

If ports 3000, 8000, 5432, or 6379 are taken:

1. Stop conflicting services
2. Or modify ports in `docker-compose.yml`

## Next Steps

- **Read the API docs**: <http://localhost:8000/api/docs>
- **Explore the codebase**: See `forge_platform/README.md`
- **Configure MLflow**: See MLflow integration guide
- **Set up CI/CD**: Configure GitHub Actions
- **Deploy to production**: See Kubernetes deployment guide

## Quick Reference

### Useful Commands

```bash
# Start all services
cd forge_platform/infra/docker && docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend

# Access database
docker-compose exec postgres psql -U forgetrace -d forgetrace_platform

# Access Redis CLI
docker-compose exec redis redis-cli

# Run backend tests
cd forge_platform/backend && pytest

# Run frontend tests
cd forge_platform/frontend && npm test

# Build production images
docker-compose build
```

### Directory Structure

```text
forge_platform/
├── backend/          # FastAPI application
│   ├── app/          # Application code
│   ├── alembic/      # Database migrations
│   ├── tests/        # Backend tests
│   └── requirements.txt
├── frontend/         # React application
│   ├── src/          # Frontend code
│   ├── public/       # Static assets
│   └── package.json
└── infra/            # Infrastructure
    ├── docker/       # Docker Compose
    └── k8s/          # Kubernetes manifests
```

## Getting Help

- Check the [main README](README.md) for detailed documentation
- Review [API documentation](<http://localhost:8000/api/docs>)
- Open an issue on GitHub
- Contact support: support@forgetrace.com

---

**Ready to build?** Start by creating your first account and connecting a repository!
