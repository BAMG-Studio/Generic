"""
FastAPI Application Entry Point
Multi-tenant ForgeTrace SaaS Platform
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .core.config import settings
from .api import auth, scans, repositories, consent, tokens, oauth_routes
from .api import audits, usage
from .middleware.rate_limit import RateLimitMiddleware, RateLimitConfig


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    print(f"   Environment: {settings.ENV}")
    print(f"   Multi-tenancy mode: {settings.TENANT_ISOLATION_MODE}")
    print(f"   API docs: {'/api/docs' if settings.DEBUG else 'disabled'}")
    
    yield
    
    # Shutdown
    print(f"👋 {settings.APP_NAME} shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    config=RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=1000,
        requests_per_day=10000
    )
)

# Security middleware
if settings.ENV == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.forgetrace.com", "forgetrace.com", "*.forgetrace.pro", "forgetrace.pro"]
    )

# Include routers
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(oauth_routes.router, prefix=settings.API_PREFIX)
app.include_router(scans.router, prefix=settings.API_PREFIX)
app.include_router(repositories.router, prefix=settings.API_PREFIX)
app.include_router(consent.router, prefix=settings.API_PREFIX)
app.include_router(tokens.router, prefix=settings.API_PREFIX)
app.include_router(audits.router, prefix=settings.API_PREFIX, tags=["audits"])
app.include_router(usage.router, prefix=settings.API_PREFIX, tags=["usage"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENV,
    }


@app.get("/")
async def root():
    """API root"""
    return {
        "message": "ForgeTrace Platform API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs" if settings.DEBUG else "Documentation disabled in production",
    }
