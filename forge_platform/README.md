# ForgeTrace Control Center

**Production-ready multi-domain platform for IP audit services**

## 🚀 Quick Start

```bash
# Deploy locally
./deploy.sh development

# Access at:
# - Frontend: http://localhost:5173
# - Backend: http://localhost:8000
# - API Docs: http://localhost:8000/api/docs

# Default admin:
# Email: admin@forgetrace.pro
# Password: admin123
```

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get running in 5 minutes
- **[Production Deployment](PRODUCTION_DEPLOY.md)** - Deploy to forgetrace.pro
- **[Implementation Complete](IMPLEMENTATION_COMPLETE.md)** - What's been built
- **[Architecture](../docs/CONTROL_CENTER_ARCHITECTURE.md)** - System design
- **[Control Center README](CONTROL_CENTER_README.md)** - Full platform docs

## ✨ Features

- ✅ **Dual Authentication** - Token-based for clients, credentials for management
- ✅ **OAuth Integration** - GitHub and Google sign-in
- ✅ **Role-Based Access** - Super Admin, Tenant Admin, User, Viewer
- ✅ **API Tokens** - Secure ftk_ prefixed tokens with scoping
- ✅ **Subscription Tiers** - Free, Professional, Enterprise
- ✅ **Docker Deployment** - One-command setup
- ✅ **CLI Tools** - User and token management
- ✅ **Production Ready** - SSL, monitoring, backups

## 🏗️ Architecture

```
www.forgetrace.pro    → Public marketing site
app.forgetrace.pro    → Control center dashboard
api.forgetrace.pro    → Backend API
```

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python)
- PostgreSQL
- Redis
- JWT + OAuth

**Frontend:**
- React + TypeScript
- Vite
- Tailwind CSS

**DevOps:**
- Docker + Docker Compose
- Nginx
- Let's Encrypt SSL

## 📋 Requirements

- Docker & Docker Compose
- 8GB RAM minimum
- 50GB storage

## 🔧 CLI Commands

```bash
# Create user
docker-compose exec backend python cli.py create-user

# Create API token
docker-compose exec backend python cli.py create-token --email user@example.com

# List users
docker-compose exec backend python cli.py list-users

# List tokens
docker-compose exec backend python cli.py list-tokens --email user@example.com

# Revoke token
docker-compose exec backend python cli.py revoke-token --prefix ftk_xxxxxxxx
```

## 🔐 OAuth Configuration

### GitHub OAuth
- Client ID: `0v231iVg8ui90ZAI4Km8`
- Callback: `https://api.forgetrace.pro/api/v1/auth/callback/github`

### Google OAuth
- Client ID: `163606189898-uts4nnb1u38b13785n7gmgq0j20m79ed.apps.googleusercontent.com`
- Callback: `https://api.forgetrace.pro/api/v1/auth/callback/google`

## 📊 Project Structure

```
forge_platform/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── models/      # Database models
│   │   ├── middleware/  # Auth & RBAC
│   │   └── core/        # Configuration
│   ├── cli.py           # Management CLI
│   └── requirements.txt
├── frontend/            # React application
│   ├── src/
│   │   ├── pages/       # Login, portals
│   │   ├── components/  # UI components
│   │   └── store/       # State management
│   └── package.json
├── infra/               # Infrastructure
│   ├── docker/          # Dockerfiles
│   └── k8s/             # Kubernetes configs
├── deploy.sh            # Deployment script
└── docker-compose.yml   # Docker orchestration
```

## 🚀 Deployment

### Local Development
```bash
./deploy.sh development
```

### Production
```bash
# See PRODUCTION_DEPLOY.md for full guide
./deploy.sh production
```

## 📞 Support

- **Email**: hello@bamgstudio.com
- **Website**: https://bamgstudio.com
- **Documentation**: See docs/ folder

## 📄 License

Proprietary - All Rights Reserved

Built by Peter Kolawole, BAMG Studio LLC

---

**ForgeTrace Control Center v1.0.0**

🎉 **Ready for production deployment!**
