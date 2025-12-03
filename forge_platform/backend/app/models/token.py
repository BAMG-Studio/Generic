"""
API Token Models for programmatic access
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from ..db.base import Base
import secrets
import hashlib


class APIToken(Base):
    """Personal access tokens for API authentication"""
    __tablename__ = "api_tokens"
    
    # Ownership
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Token identification
    name = Column(String, nullable=False)  # User-friendly name
    token_prefix = Column(String, nullable=False, index=True)  # First 8 chars for display
    hashed_token = Column(String, nullable=False, unique=True, index=True)  # SHA-256 hash
    
    # Scopes & permissions
    scopes = Column(Text, nullable=False)  # Comma-separated: read:reports,write:audits
    
    # Lifecycle
    expires_at = Column(String, nullable=True)  # ISO timestamp or null for no expiration
    last_used_at = Column(String, nullable=True)  # ISO timestamp of last API call
    revoked_at = Column(String, nullable=True)  # ISO timestamp when revoked
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_by_ip = Column(String, nullable=True)
    last_used_ip = Column(String, nullable=True)
    
    @staticmethod
    def generate_token() -> tuple[str, str, str]:
        """
        Generate a new API token.
        Returns: (full_token, prefix, hashed_token)
        - full_token: The actual token to show to user once (ftk_...)
        - prefix: First 8 chars for display in UI
        - hashed_token: SHA-256 hash to store in DB
        """
        # Generate random token
        random_part = secrets.token_urlsafe(32)
        full_token = f"ftk_{random_part}"
        
        # Create prefix for display
        prefix = full_token[:12]  # "ftk_" + first 8 chars
        
        # Hash for storage
        hashed = hashlib.sha256(full_token.encode()).hexdigest()
        
        return full_token, prefix, hashed
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token for comparison"""
        return hashlib.sha256(token.encode()).hexdigest()


class TokenUsageEvent(Base):
    """Track API token usage for billing and analytics"""
    __tablename__ = "token_usage_events"
    
    # Relations
    token_id = Column(String, ForeignKey("api_tokens.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Request details
    endpoint = Column(String, nullable=False)  # /api/v1/audits
    method = Column(String, nullable=False)  # GET, POST, etc
    status_code = Column(Integer, nullable=False)  # 200, 404, etc
    
    # Metering
    files_scanned = Column(Integer, default=0)  # For billable unit tracking
    storage_bytes = Column(Integer, default=0)
    
    # Metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    request_id = Column(String, nullable=True, index=True)  # For correlation
    
    # Note: created_at from Base is the event timestamp


class UsageAggregate(Base):
    """Daily aggregates for quota enforcement and billing"""
    __tablename__ = "usage_aggregates"
    
    # Dimensions
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    period_date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    
    # Metrics
    api_requests = Column(Integer, default=0)
    files_scanned = Column(Integer, default=0)
    storage_bytes_used = Column(Integer, default=0)
    
    # Make user_id + period unique
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
