"""
ForgeTrace Platform Configuration
Multi-tenant SaaS settings with environment-based overrides
"""
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "ForgeTrace Platform"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION_USE_STRONG_RANDOM_KEY"
    JWT_SECRET: str = "CHANGE_THIS_IN_PRODUCTION_USE_STRONG_RANDOM_KEY"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://forgetrace:forgetrace@localhost:5432/forgetrace_platform"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Multi-tenancy
    TENANT_ISOLATION_MODE: str = "shared"  # shared | schema | isolated
    
    # Redis (caching & sessions)
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600
    
    # OAuth Providers
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    OAUTH_CALLBACK_URL: str = "http://localhost:8000/api/v1/auth/callback"
    
    # AWS/S3 for artifact storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_DEFAULT_REGION: str = "us-east-1"
    S3_BUCKET_SCANS: str = "forgetrace-scans"
    S3_BUCKET_MODELS: str = "forgetrace-models"
    
    # MLflow Integration
    MLFLOW_TRACKING_URI: Optional[str] = None
    MLFLOW_USERNAME: Optional[str] = None
    MLFLOW_PASSWORD: Optional[str] = None
    MLFLOW_EXPERIMENT_NAME: str = "forgetrace-production"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://app.forgetrace.com",
        "https://www.forgetrace.pro",
        "https://app.forgetrace.pro",
    ]
    
    # Email (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@forgetrace.com"
    
    # Feature Flags
    ENABLE_SIGNUP: bool = True
    ENABLE_ML_CLASSIFICATION: bool = True
    ENABLE_WEBHOOKS: bool = True
    REQUIRE_EMAIL_VERIFICATION: bool = False
    
    # Scan Processing
    MAX_CONCURRENT_SCANS: int = 5
    SCAN_TIMEOUT_MINUTES: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
