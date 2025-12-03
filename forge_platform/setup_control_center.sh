#!/bin/bash

# ForgeTrace Control Center Setup Script
# This script sets up the development environment for the control center

set -e

echo "🚀 ForgeTrace Control Center Setup"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from correct directory
if [ ! -f "setup_control_center.sh" ]; then
    echo "❌ Please run this script from the forge_platform directory"
    exit 1
fi

echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

# Check for required tools
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm is required but not installed."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "⚠️  Docker not found. You'll need it for PostgreSQL and Redis."; }

echo -e "${GREEN}✓ Prerequisites check complete${NC}"
echo ""

# Backend setup
echo -e "${BLUE}Step 2: Setting up backend...${NC}"

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit backend/.env with your configuration${NC}"
fi

echo -e "${GREEN}✓ Backend setup complete${NC}"
echo ""

cd ..

# Frontend setup
echo -e "${BLUE}Step 3: Setting up frontend...${NC}"

cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install --silent

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit frontend/.env with your configuration${NC}"
fi

echo -e "${GREEN}✓ Frontend setup complete${NC}"
echo ""

cd ..

# Database setup
echo -e "${BLUE}Step 4: Setting up database...${NC}"

# Check if Docker is available
if command -v docker >/dev/null 2>&1; then
    echo "Starting PostgreSQL and Redis with Docker..."
    
    # Start PostgreSQL
    if ! docker ps | grep -q forgetrace-postgres; then
        docker run -d \
            --name forgetrace-postgres \
            -e POSTGRES_USER=forgetrace \
            -e POSTGRES_PASSWORD=forgetrace \
            -e POSTGRES_DB=forgetrace_platform \
            -p 5432:5432 \
            postgres:15-alpine
        echo "PostgreSQL started on port 5432"
    else
        echo "PostgreSQL already running"
    fi
    
    # Start Redis
    if ! docker ps | grep -q forgetrace-redis; then
        docker run -d \
            --name forgetrace-redis \
            -p 6379:6379 \
            redis:7-alpine
        echo "Redis started on port 6379"
    else
        echo "Redis already running"
    fi
    
    # Wait for PostgreSQL to be ready
    echo "Waiting for PostgreSQL to be ready..."
    sleep 5
    
    # Run migrations
    echo "Running database migrations..."
    cd backend
    source venv/bin/activate
    alembic upgrade head
    cd ..
    
    echo -e "${GREEN}✓ Database setup complete${NC}"
else
    echo -e "${YELLOW}⚠️  Docker not available. Please set up PostgreSQL and Redis manually.${NC}"
    echo "   PostgreSQL: localhost:5432, database: forgetrace_platform"
    echo "   Redis: localhost:6379"
fi

echo ""

# Summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure environment variables:"
echo "   - Edit backend/.env"
echo "   - Edit frontend/.env"
echo ""
echo "2. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "3. Start the frontend (in a new terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Access the application:"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "5. Create your first user:"
echo "   curl -X POST http://localhost:8000/api/v1/auth/register \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"email\":\"admin@forgetrace.pro\",\"password\":\"SecurePass123!\",\"full_name\":\"Admin\"}'"
echo ""
echo "📚 Documentation:"
echo "   - Architecture: docs/CONTROL_CENTER_ARCHITECTURE.md"
echo "   - Implementation: docs/CONTROL_CENTER_IMPLEMENTATION.md"
echo "   - README: forge_platform/CONTROL_CENTER_README.md"
echo ""
echo "Need help? Email: hello@bamgstudio.com"
echo ""
