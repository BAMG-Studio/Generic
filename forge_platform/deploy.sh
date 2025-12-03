#!/bin/bash

# ForgeTrace Control Center Deployment Script

set -e

echo "🚀 ForgeTrace Control Center Deployment"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check environment
if [ -z "$1" ]; then
    echo -e "${RED}Error: Environment not specified${NC}"
    echo "Usage: ./deploy.sh [development|production]"
    exit 1
fi

ENV=$1

echo -e "${BLUE}Deploying to: ${ENV}${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker is required${NC}"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}Docker Compose is required${NC}"; exit 1; }

echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# Step 2: Setup environment files
echo -e "${BLUE}Step 2: Setting up environment files...${NC}"

if [ "$ENV" = "production" ]; then
    if [ ! -f "backend/.env.production" ]; then
        echo -e "${RED}Error: backend/.env.production not found${NC}"
        exit 1
    fi
    cp backend/.env.production backend/.env
    cp frontend/.env.production frontend/.env
else
    if [ ! -f "backend/.env.development" ]; then
        echo -e "${RED}Error: backend/.env.development not found${NC}"
        exit 1
    fi
    cp backend/.env.development backend/.env
    cp frontend/.env.development frontend/.env
fi

echo -e "${GREEN}✓ Environment files configured${NC}"
echo ""

# Step 3: Build containers
echo -e "${BLUE}Step 3: Building Docker containers...${NC}"

docker-compose build

echo -e "${GREEN}✓ Containers built${NC}"
echo ""

# Step 4: Start services
echo -e "${BLUE}Step 4: Starting services...${NC}"

docker-compose up -d postgres redis

echo "Waiting for database to be ready..."
sleep 10

echo -e "${GREEN}✓ Database and Redis started${NC}"
echo ""

# Step 5: Run migrations
echo -e "${BLUE}Step 5: Running database migrations...${NC}"

docker-compose run --rm backend alembic upgrade head

echo -e "${GREEN}✓ Migrations complete${NC}"
echo ""

# Step 6: Create super admin (development only)
if [ "$ENV" = "development" ]; then
    echo -e "${BLUE}Step 6: Creating super admin user...${NC}"
    
    docker-compose run --rm backend python -c "
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole, Tenant, TenantTier
import bcrypt

async def create_admin():
    async with AsyncSessionLocal() as db:
        # Create tenant
        tenant = Tenant(
            name='BAMG Studio',
            slug='bamg-studio',
            tier=TenantTier.ENTERPRISE
        )
        db.add(tenant)
        await db.flush()
        
        # Create admin user
        hashed = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode()
        admin = User(
            email='admin@forgetrace.pro',
            hashed_password=hashed,
            full_name='System Administrator',
            role=UserRole.SUPER_ADMIN,
            tenant_id=tenant.id,
            is_active=True,
            is_verified=True
        )
        db.add(admin)
        await db.commit()
        print('✓ Super admin created: admin@forgetrace.pro / admin123')

asyncio.run(create_admin())
" || echo "Admin user may already exist"

    echo -e "${GREEN}✓ Super admin ready${NC}"
    echo ""
fi

# Step 7: Start all services
echo -e "${BLUE}Step 7: Starting all services...${NC}"

docker-compose up -d

echo -e "${GREEN}✓ All services started${NC}"
echo ""

# Step 8: Health check
echo -e "${BLUE}Step 8: Running health checks...${NC}"

sleep 5

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend API is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Backend API not responding yet (may need more time)${NC}"
fi

echo ""

# Summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Services:"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/api/docs"
echo "  - Frontend: http://localhost:5173"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo ""

if [ "$ENV" = "development" ]; then
    echo "Super Admin Credentials:"
    echo "  Email: admin@forgetrace.pro"
    echo "  Password: admin123"
    echo ""
fi

echo "View logs:"
echo "  docker-compose logs -f"
echo ""
echo "Stop services:"
echo "  docker-compose down"
echo ""
