"""
OAuth Authentication Endpoints
Handles OAuth login with GitHub and Google
"""
import secrets
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..services.oauth import oauth_service
from ..models.user import User, Tenant, OAuthToken
from ..core.security import create_access_token, create_refresh_token
from sqlalchemy import select

router = APIRouter()


# In-memory state storage (use Redis in production)
oauth_states = {}


@router.get("/oauth/{provider}")
async def oauth_login(provider: str):
    """
    Initiate OAuth login flow
    
    Args:
        provider: OAuth provider (github, google)
    """
    if not oauth_service.is_enabled(provider):
        raise HTTPException(
            status_code=400,
            detail=f"OAuth provider '{provider}' is not configured"
        )
    
    oauth_provider = oauth_service.get_provider(provider)
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = provider
    
    # Get authorization URL
    auth_url = oauth_provider.get_authorization_url(state)
    
    return RedirectResponse(url=auth_url)


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth callback endpoint
    
    Args:
        provider: OAuth provider name
        code: Authorization code from provider
        state: CSRF protection state
    """
    # Verify state
    if state not in oauth_states or oauth_states[state] != provider:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Remove used state
    del oauth_states[state]
    
    # Get OAuth provider
    oauth_provider = oauth_service.get_provider(provider)
    if not oauth_provider:
        raise HTTPException(status_code=400, detail="OAuth provider not configured")
    
    # Exchange code for token
    token_data = await oauth_provider.exchange_code_for_token(code)
    if not token_data:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")
    
    access_token = token_data.get('access_token')
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received")
    
    # Get user info from provider
    user_info = await oauth_provider.get_user_info(access_token)
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to get user info")
    
    email = user_info.get('email')
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by OAuth provider")
    
    # Check if user exists
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new tenant and user
        tenant = Tenant(
            name=f"{user_info.get('name', email.split('@')[0])}'s Organization",
            slug=email.split('@')[0].lower().replace('.', '-'),
            tier="free"
        )
        db.add(tenant)
        await db.flush()
        
        user = User(
            email=email,
            full_name=user_info.get('name'),
            tenant_id=tenant.id,
            role="tenant_admin",
            is_active=True,
            hashed_password=""  # No password for OAuth users
        )
        db.add(user)
        await db.flush()
    
    # Store/update OAuth token
    oauth_token_result = await db.execute(
        select(OAuthToken).where(
            OAuthToken.user_id == user.id,
            OAuthToken.provider == provider
        )
    )
    oauth_token = oauth_token_result.scalar_one_or_none()
    
    if oauth_token:
        oauth_token.access_token = access_token
        oauth_token.refresh_token = token_data.get('refresh_token')
        oauth_token.expires_at = None  # Set based on expires_in if available
    else:
        oauth_token = OAuthToken(
            user_id=user.id,
            provider=provider,
            provider_user_id=user_info.get('id'),
            access_token=access_token,
            refresh_token=token_data.get('refresh_token')
        )
        db.add(oauth_token)
    
    await db.commit()
    
    # Create JWT tokens for our platform
    platform_access_token = create_access_token({"sub": user.email})
    platform_refresh_token = create_refresh_token({"sub": user.email})
    
    # Redirect to frontend with tokens
    frontend_url = "http://localhost:3001"  # TODO: Get from config
    redirect_url = f"{frontend_url}/oauth/callback?access_token={platform_access_token}&refresh_token={platform_refresh_token}"
    
    return RedirectResponse(url=redirect_url)


@router.get("/providers")
async def get_oauth_providers():
    """Get list of enabled OAuth providers"""
    return {
        "providers": oauth_service.get_enabled_providers()
    }
