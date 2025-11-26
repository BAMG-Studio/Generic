"""
OAuth Service for ForgeTrace Platform
Handles OAuth authentication with GitHub and Google
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import httpx
from jose import jwt
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token

logger = logging.getLogger(__name__)


class OAuthProvider:
    """Base OAuth provider interface"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, state: str) -> str:
        """Get OAuth authorization URL"""
        raise NotImplementedError
    
    async def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        raise NotImplementedError
    
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from provider"""
        raise NotImplementedError


class GitHubOAuthProvider(OAuthProvider):
    """GitHub OAuth 2.0 provider"""
    
    AUTHORIZATION_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_API_URL = "https://api.github.com/user"
    USER_EMAILS_URL = "https://api.github.com/user/emails"
    
    def get_authorization_url(self, state: str) -> str:
        """Generate GitHub OAuth authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'read:user user:email',
            'state': state
        }
        
        query_string = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTHORIZATION_URL}?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for GitHub access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.TOKEN_URL,
                    headers={'Accept': 'application/json'},
                    data={
                        'client_id': self.client_id,
                        'client_secret': self.client_secret,
                        'code': code,
                        'redirect_uri': self.redirect_uri
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"GitHub token exchange failed: {response.text}")
                    return None
                
                return response.json()
                
        except Exception as e:
            logger.error(f"GitHub OAuth token exchange error: {e}")
            return None
    
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get GitHub user information"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                }
                
                # Get user profile
                user_response = await client.get(self.USER_API_URL, headers=headers)
                if user_response.status_code != 200:
                    return None
                
                user_data = user_response.json()
                
                # Get primary email
                emails_response = await client.get(self.USER_EMAILS_URL, headers=headers)
                if emails_response.status_code == 200:
                    emails = emails_response.json()
                    primary_email = next(
                        (e['email'] for e in emails if e['primary'] and e['verified']),
                        user_data.get('email')
                    )
                else:
                    primary_email = user_data.get('email')
                
                return {
                    'id': str(user_data['id']),
                    'email': primary_email,
                    'name': user_data.get('name') or user_data.get('login'),
                    'avatar_url': user_data.get('avatar_url'),
                    'provider': 'github'
                }
                
        except Exception as e:
            logger.error(f"GitHub user info retrieval error: {e}")
            return None


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth 2.0 provider"""
    
    AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_authorization_url(self, state: str) -> str:
        """Generate Google OAuth authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        query_string = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTHORIZATION_URL}?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for Google access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        'client_id': self.client_id,
                        'client_secret': self.client_secret,
                        'code': code,
                        'grant_type': 'authorization_code',
                        'redirect_uri': self.redirect_uri
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Google token exchange failed: {response.text}")
                    return None
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Google OAuth token exchange error: {e}")
            return None
    
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get Google user information"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.USER_INFO_URL,
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                
                if response.status_code != 200:
                    return None
                
                user_data = response.json()
                
                return {
                    'id': user_data['id'],
                    'email': user_data['email'],
                    'name': user_data.get('name'),
                    'avatar_url': user_data.get('picture'),
                    'provider': 'google'
                }
                
        except Exception as e:
            logger.error(f"Google user info retrieval error: {e}")
            return None


class OAuthService:
    """Main OAuth service for managing providers"""
    
    def __init__(self):
        """Initialize OAuth providers"""
        self.providers: Dict[str, OAuthProvider] = {}
        
        # Initialize GitHub OAuth
        if settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET:
            self.providers['github'] = GitHubOAuthProvider(
                client_id=settings.GITHUB_CLIENT_ID,
                client_secret=settings.GITHUB_CLIENT_SECRET,
                redirect_uri=f"{settings.OAUTH_CALLBACK_URL}/github"
            )
            logger.info("GitHub OAuth provider initialized")
        
        # Initialize Google OAuth
        if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
            self.providers['google'] = GoogleOAuthProvider(
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                redirect_uri=f"{settings.OAUTH_CALLBACK_URL}/google"
            )
            logger.info("Google OAuth provider initialized")
    
    def get_provider(self, provider_name: str) -> Optional[OAuthProvider]:
        """Get OAuth provider by name"""
        return self.providers.get(provider_name)
    
    def is_enabled(self, provider_name: str) -> bool:
        """Check if provider is enabled"""
        return provider_name in self.providers
    
    def get_enabled_providers(self) -> list[str]:
        """Get list of enabled provider names"""
        return list(self.providers.keys())


# Global instance
oauth_service = OAuthService()
