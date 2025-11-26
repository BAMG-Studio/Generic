#!/bin/bash
set -e

echo "🚀 ForgeTrace Platform - Quick Setup"
echo "===================================="
echo ""

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }

echo "✅ Prerequisites check passed"
echo ""

# Navigate to project root
cd "$(dirname "$0")"

# Backend setup
echo "📦 Setting up backend..."
cd forge_platform/backend

if [ ! -f ".env" ]; then
    echo "   Creating backend .env from example..."
    cp .env.example .env
    echo "   ⚠️  Please edit forge_platform/backend/.env with your configuration"
fi

# Frontend setup
echo "📦 Setting up frontend..."
cd ../frontend

if [ ! -f ".env" ]; then
    echo "   Creating frontend .env..."
    echo "VITE_API_URL=http://localhost:8000/api/v1" > .env
fi

# Docker compose setup
echo "🐳 Setting up Docker environment..."
cd ../infra/docker

if [ ! -f ".env" ]; then
    echo "   Creating docker .env..."
    cat > .env << EOF
ENV=development
DB_PASSWORD=forgetrace_dev_password
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
EOF
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Review and update configuration files:"
echo "   - forge_platform/backend/.env"
echo "   - forge_platform/infra/docker/.env"
echo ""
echo "2. Start the platform:"
echo "   cd forge_platform/infra/docker"
echo "   docker-compose up -d"
echo ""
echo "3. Initialize database:"
echo "   cd forge_platform/backend"
echo "   pip install -r requirements.txt"
echo "   alembic upgrade head"
echo ""
echo "4. Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/api/docs"
echo ""
echo "📚 See forge_platform/README.md for full documentation"
