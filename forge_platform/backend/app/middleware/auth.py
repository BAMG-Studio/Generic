"""
Authentication and Authorization Middleware
"""
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import jwt
from datetime import datetime

from ..core.config import settings
from ..db.session import get_db
from ..models.user import User, UserRole
from ..models.token import APIToken
from ..models.rbac import has_permission, has_scope, Permission


security = HTTPBearer()


class AuthContext:
    """Authentication context for requests"""
    def __init__(
        self,
        user_id: str,
        tenant_id: str,
        role: UserRole,
        auth_type: str,  # "jwt" or "token"
        token_id: Optional[str] = None,
        scopes: Optional[str] = None,
    ):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.role = role
        self.auth_type = auth_type
        self.token_id = token_id
        self.scopes = scopes or ""
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has permission"""
        return has_permission(self.role.value, permission)
    
    def has_scope(self, scope: str) -> bool:
        """Check if token has scope"""
        if self.auth_type == "jwt":
            return True  # JWT users have full access based on role
        return has_scope(self.scopes, scope)


async def get_current_user_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    """
    Validate JWT token and return auth context.
    Used for management users with email/password or OAuth login.
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Fetch user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return AuthContext(
        user_id=user.id,
        tenant_id=user.tenant_id,
        role=user.role,
        auth_type="jwt"
    )


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    """
    Validate API token and return auth context.
    Used for client users with purchased API tokens.
    """
    token = credentials.credentials
    
    # Check if token starts with ftk_ prefix
    if not token.startswith("ftk_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    
    # Hash token for lookup
    hashed = APIToken.hash_token(token)
    
    # Find token in database
    result = await db.execute(
        select(APIToken).where(
            APIToken.hashed_token == hashed,
            APIToken.is_active == True
        )
    )
    api_token = result.scalar_one_or_none()
    
    if api_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked token"
        )
    
    # Check expiration
    if api_token.expires_at:
        expires = datetime.fromisoformat(api_token.expires_at)
        if datetime.utcnow() > expires:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
    
    # Update last used timestamp
    api_token.last_used_at = datetime.utcnow().isoformat()
    await db.commit()
    
    # Fetch user
    result = await db.execute(select(User).where(User.id == api_token.user_id))
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return AuthContext(
        user_id=user.id,
        tenant_id=user.tenant_id,
        role=user.role,
        auth_type="token",
        token_id=api_token.id,
        scopes=api_token.scopes
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    """
    Universal authentication - supports both JWT and API tokens.
    Automatically detects token type and validates accordingly.
    """
    token = credentials.credentials
    
    # Detect token type
    if token.startswith("ftk_"):
        return await get_current_user_token(credentials, db)
    else:
        return await get_current_user_jwt(credentials, db)


def require_permission(permission: Permission):
    """
    Dependency to require specific permission.
    Usage: auth: AuthContext = Depends(require_permission(Permission.READ_AUDITS))
    """
    async def permission_checker(
        auth: AuthContext = Depends(get_current_user)
    ) -> AuthContext:
        if not auth.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission.value}"
            )
        return auth
    
    return permission_checker


def require_scope(scope: str):
    """
    Dependency to require specific scope (for API tokens).
    Usage: auth: AuthContext = Depends(require_scope("write:audits"))
    """
    async def scope_checker(
        auth: AuthContext = Depends(get_current_user)
    ) -> AuthContext:
        if not auth.has_scope(scope):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scope: {scope}"
            )
        return auth
    
    return scope_checker


def require_role(allowed_roles: list[UserRole]):
    """
    Dependency to require specific role.
    Usage: auth: AuthContext = Depends(require_role([UserRole.SUPER_ADMIN]))
    """
    async def role_checker(
        auth: AuthContext = Depends(get_current_user)
    ) -> AuthContext:
        if auth.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient privileges"
            )
        return auth
    
    return role_checker
