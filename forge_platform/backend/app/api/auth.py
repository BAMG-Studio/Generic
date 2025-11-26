"""
Authentication API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from ..db.session import get_db
from ..models.user import User, Tenant, UserRole, TenantTier
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
)
from ..auth.dependencies import get_current_user
import uuid

router = APIRouter(prefix="/auth", tags=["authentication"])


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    tenant_id: str


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    data: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create new user account and tenant"""
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create tenant
    tenant_id = str(uuid.uuid4())
    tenant_slug = data.company_name.lower().replace(" ", "-")
    
    tenant = Tenant(
        id=tenant_id,
        tenant_id=tenant_id,
        name=data.company_name,
        slug=tenant_slug,
        tier=TenantTier.FREE,
    )
    db.add(tenant)
    
    # Create user
    user = User(
        tenant_id=tenant_id,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        role=UserRole.TENANT_ADMIN,
        is_verified=True,  # Skip email verification for now
    )
    db.add(user)
    
    await db.commit()
    await db.refresh(user)
    
    # Create tokens
    access_token = create_access_token({
        "sub": user.id,
        "tenant_id": tenant_id,
        "role": user.role.value,
    })
    
    refresh_token = create_refresh_token({
        "sub": user.id,
        "tenant_id": tenant_id,
    })
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        tenant_id=tenant_id,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return tokens"""
    
    # Find user
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token({
        "sub": user.id,
        "tenant_id": user.tenant_id,
        "role": user.role.value,
    })
    
    refresh_token = create_refresh_token({
        "sub": user.id,
        "tenant_id": user.tenant_id,
    })
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        tenant_id=user.tenant_id,
    )


@router.get("/me")
async def get_current_user_info(
    user: User = Depends(get_current_user)
):
    """Get current user information"""
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "tenant_id": user.tenant_id,
        "is_verified": user.is_verified,
    }
