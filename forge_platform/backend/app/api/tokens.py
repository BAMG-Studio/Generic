from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import secrets
import hashlib

from ..db.session import get_db
from ..models.user import User
from ..middleware.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class TokenCreate(BaseModel):
    name: str
    scopes: List[str] = ["read:audits", "write:audits"]

class TokenResponse(BaseModel):
    id: str
    name: str
    token: str  # Only shown once
    createdAt: str
    lastUsed: str | None

class TokenListItem(BaseModel):
    id: str
    name: str
    token: str  # Masked
    createdAt: str
    lastUsed: str | None

# Temporary in-memory storage (replace with database)
tokens_store = {}

def generate_token() -> str:
    """Generate a secure API token"""
    return f"ftk_{secrets.token_urlsafe(32)}"

def hash_token(token: str) -> str:
    """Hash token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()

@router.post("/tokens", response_model=TokenResponse)
async def create_token(
    token_data: TokenCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new API token"""
    token = generate_token()
    token_hash = hash_token(token)
    token_id = f"tok_{datetime.utcnow().timestamp()}"
    
    token_record = {
        'id': token_id,
        'name': token_data.name,
        'tokenHash': token_hash,
        'token': token,  # Store temporarily for response
        'createdAt': datetime.utcnow().isoformat(),
        'lastUsed': None,
        'userId': current_user.id,
        'scopes': token_data.scopes
    }
    
    tokens_store[token_id] = token_record
    
    # Return full token (only time it's visible)
    return TokenResponse(
        id=token_id,
        name=token_data.name,
        token=token,
        createdAt=token_record['createdAt'],
        lastUsed=None
    )

@router.get("/tokens", response_model=List[TokenListItem])
async def list_tokens(
    current_user: User = Depends(get_current_user)
):
    """List all tokens for current user"""
    user_tokens = [
        TokenListItem(
            id=token['id'],
            name=token['name'],
            token=f"ftk_{'*' * 15}",  # Masked
            createdAt=token['createdAt'],
            lastUsed=token['lastUsed']
        )
        for token in tokens_store.values()
        if token.get('userId') == current_user.id
    ]
    
    return user_tokens

@router.get("/tokens/{token_id}", response_model=TokenListItem)
async def get_token(
    token_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get token details"""
    token = tokens_store.get(token_id)
    
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    if token.get('userId') != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return TokenListItem(
        id=token['id'],
        name=token['name'],
        token=f"ftk_{'*' * 15}",
        createdAt=token['createdAt'],
        lastUsed=token['lastUsed']
    )

@router.delete("/tokens/{token_id}")
async def revoke_token(
    token_id: str,
    current_user: User = Depends(get_current_user)
):
    """Revoke an API token"""
    token = tokens_store.get(token_id)
    
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    if token.get('userId') != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    del tokens_store[token_id]
    
    return {"message": "Token revoked"}

@router.post("/tokens/{token_id}/refresh")
async def refresh_token(
    token_id: str,
    current_user: User = Depends(get_current_user)
):
    """Refresh token last used timestamp"""
    token = tokens_store.get(token_id)
    
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    if token.get('userId') != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    token['lastUsed'] = datetime.utcnow().isoformat()
    
    return {"message": "Token refreshed"}
