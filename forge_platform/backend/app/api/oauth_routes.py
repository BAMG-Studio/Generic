"""
OAuth authentication routes (GitHub, Google)
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
from datetime import datetime

from ..db.session import get_db
from ..core.config import settings
from ..models.user import User, UserRole, Tenant, TenantTier
from ..api.auth import create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["oauth"])


@router.get("/github")
async def github_login():
    """Initiate GitHub OAuth flow"""
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        f"&scope=read:user user:email"
    )
    return RedirectResponse(github_auth_url)


@router.get("/callback/github")
async def github_callback(code: str, db: AsyncSession = Depends(get_db)):
    """Handle GitHub OAuth callback"""
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"}
        )
        token_data = token_response.json()
        
        if "access_token" not in token_data:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        github_token = token_data["access_token"]
        
        # Get user info
        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {github_token}"}
        )
        github_user = user_response.json()
        
        # Get user email
        email_response = await client.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"Bearer {github_token}"}
        )
        emails = email_response.json()
        primary_email = next((e["email"] for e in emails if e["primary"]), emails[0]["email"])
    
    # Find or create user
    result = await db.execute(select(User).where(User.email == primary_email))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create tenant
        tenant = Tenant(
            name=f"{github_user['name'] or github_user['login']}'s Organization",
            slug=github_user['login'],
            tier=TenantTier.FREE
        )
        db.add(tenant)
        await db.flush()
        
        # Create user
        user = User(
            email=primary_email,
            full_name=github_user.get("name") or github_user["login"],
            role=UserRole.USER,
            tenant_id=tenant.id,
            oauth_provider="github",
            oauth_id=str(github_user["id"]),
            oauth_data={"login": github_user["login"], "avatar_url": github_user.get("avatar_url")},
            is_active=True,
            is_verified=True
        )
        db.add(user)
    else:
        # Update OAuth info
        user.oauth_provider = "github"
        user.oauth_id = str(github_user["id"])
        user.last_login_at = datetime.utcnow().isoformat()
        user.login_count = str(int(user.login_count or "0") + 1)
    
    await db.commit()
    await db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    # Redirect to frontend with tokens
    redirect_url = f"{settings.FRONTEND_URL}/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
    return RedirectResponse(redirect_url)


@router.get("/google")
async def google_login():
    """Initiate Google OAuth flow"""
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid email profile"
    )
    return RedirectResponse(google_auth_url)


@router.get("/callback/google")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth callback"""
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            }
        )
        token_data = token_response.json()
        
        if "access_token" not in token_data:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        google_token = token_data["access_token"]
        
        # Get user info
        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {google_token}"}
        )
        google_user = user_response.json()
    
    # Find or create user
    result = await db.execute(select(User).where(User.email == google_user["email"]))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create tenant
        tenant = Tenant(
            name=f"{google_user['name']}'s Organization",
            slug=google_user["email"].split('@')[0],
            tier=TenantTier.FREE
        )
        db.add(tenant)
        await db.flush()
        
        # Create user
        user = User(
            email=google_user["email"],
            full_name=google_user["name"],
            role=UserRole.USER,
            tenant_id=tenant.id,
            oauth_provider="google",
            oauth_id=google_user["id"],
            oauth_data={"picture": google_user.get("picture")},
            is_active=True,
            is_verified=True
        )
        db.add(user)
    else:
        # Update OAuth info
        user.oauth_provider = "google"
        user.oauth_id = google_user["id"]
        user.last_login_at = datetime.utcnow().isoformat()
        user.login_count = str(int(user.login_count or "0") + 1)
    
    await db.commit()
    await db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    # Redirect to frontend with tokens
    redirect_url = f"{settings.FRONTEND_URL}/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
    return RedirectResponse(redirect_url)
