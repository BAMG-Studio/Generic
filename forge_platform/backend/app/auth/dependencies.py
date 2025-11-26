"""
Authentication dependencies and middleware
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..core.security import decode_token
from ..db.session import get_db
from ..models.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


async def get_tenant_context(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> tuple[str, str, str]:
    """
    Extract tenant context from JWT token
    Returns: (tenant_id, user_id, role)
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    tenant_id = payload.get("tenant_id")
    user_id = payload.get("sub")
    role = payload.get("role", "user")
    
    if not tenant_id or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid tenant context"
        )
    
    return tenant_id, user_id, role


def require_role(required_role: str):
    """Decorator to require specific role"""
    async def role_checker(
        tenant_context: tuple = Depends(get_tenant_context)
    ):
        tenant_id, user_id, role = tenant_context
        
        role_hierarchy = {
            "super_admin": 4,
            "tenant_admin": 3,
            "user": 2,
            "viewer": 1,
        }
        
        if role_hierarchy.get(role, 0) < role_hierarchy.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_role}"
            )
        
        return tenant_context
    
    return role_checker
