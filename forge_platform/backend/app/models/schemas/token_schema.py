"""
Pydantic schemas for API tokens
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class TokenScope(BaseModel):
    """Valid token scopes"""
    READ_REPORTS = "read:reports"
    WRITE_AUDITS = "write:audits"
    READ_TOKENS = "read:tokens"
    WRITE_TOKENS = "write:tokens"
    ADMIN = "admin:*"


class TokenCreate(BaseModel):
    """Request to create a new API token"""
    name: str = Field(..., min_length=1, max_length=100, description="Token display name")
    scopes: list[str] = Field(..., min_items=1, description="List of permission scopes")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Expiration in days (null for no expiration)")
    
    @field_validator('scopes')
    @classmethod
    def validate_scopes(cls, v: list[str]) -> list[str]:
        valid_scopes = {
            'read:reports', 'write:audits', 'read:tokens', 
            'write:tokens', 'admin:*'
        }
        for scope in v:
            if scope not in valid_scopes:
                raise ValueError(f"Invalid scope: {scope}")
        return v


class TokenResponse(BaseModel):
    """API token response (without secret)"""
    id: str
    name: str
    prefix: str  # e.g., "ftk_abc12345"
    scopes: list[str]
    created_at: str
    expires_at: Optional[str] = None
    last_used_at: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class TokenCreatedResponse(BaseModel):
    """Response when token is first created (includes full token once)"""
    token: str  # Full token - shown only once!
    token_info: TokenResponse


class TokenListResponse(BaseModel):
    """List of tokens"""
    tokens: list[TokenResponse]
    total: int


class TokenUsageResponse(BaseModel):
    """Usage statistics for a token or user"""
    period_start: str  # ISO date
    period_end: str
    api_requests: int
    files_scanned: int
    storage_bytes: int
    
    # Quota limits (from tenant/plan)
    api_requests_limit: Optional[int] = None
    files_scanned_limit: Optional[int] = None
    storage_bytes_limit: Optional[int] = None


class RateLimitInfo(BaseModel):
    """Rate limit headers info"""
    limit: int
    remaining: int
    reset_at: int  # Unix timestamp
    retry_after: Optional[int] = None  # Seconds to wait if limited
