"""
User and Tenant Models
"""
from sqlalchemy import Column, String, Boolean, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from ..db.base import Base
import enum


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    TENANT_ADMIN = "tenant_admin"
    USER = "user"
    VIEWER = "viewer"


class TenantTier(str, enum.Enum):
    FREE = "free"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Tenant(Base):
    """Organization/Company tenant"""
    __tablename__ = "tenants"
    
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    tier = Column(SQLEnum(TenantTier), default=TenantTier.FREE, nullable=False)
    
    # Subscription & limits
    max_repos = Column(String, default="5")  # Store as string for "unlimited"
    max_scans_per_month = Column(String, default="10")
    max_users = Column(String, default="3")
    
    # Settings
    settings = Column(JSON, default={})
    
    # Billing
    stripe_customer_id = Column(String, nullable=True)
    subscription_status = Column(String, default="trial")
    trial_ends_at = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Note: tenant_id points to itself for consistency with Base model
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.tenant_id:
            self.tenant_id = self.id


class User(Base):
    """Platform user"""
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Null for OAuth-only users
    full_name = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    
    # OAuth
    oauth_provider = Column(String, nullable=True)  # github, google, etc
    oauth_id = Column(String, nullable=True)
    oauth_data = Column(JSON, default={})
    
    # Preferences
    preferences = Column(JSON, default={})
    
    # Metadata
    last_login_at = Column(String, nullable=True)
    login_count = Column(String, default="0")


class OAuthToken(Base):
    """Store encrypted OAuth tokens for repository access"""
    __tablename__ = "oauth_tokens"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # github, gitlab, bitbucket
    
    # Encrypted tokens
    encrypted_access_token = Column(String, nullable=False)
    encrypted_refresh_token = Column(String, nullable=True)
    
    # Token metadata
    scope = Column(String, nullable=True)
    expires_at = Column(String, nullable=True)
    
    # Status
    is_valid = Column(Boolean, default=True)
