"""
Consent Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from ..db.session import get_db
from ..models.scan import ConsentRecord
from ..models.user import User
from ..auth.dependencies import get_current_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/consent", tags=["consent"])


class ConsentRequest(BaseModel):
    consent_type: str  # ML_DATA_USE, LONG_TERM_RETENTION, ANALYTICS, MARKETING
    consent_state: bool
    scan_id: Optional[str] = None


class ConsentResponse(BaseModel):
    id: str
    consent_type: str
    consent_state: bool
    created_at: str
    revoked_at: Optional[str]
    
    class Config:
        from_attributes = True


@router.post("/", response_model=ConsentResponse, status_code=status.HTTP_201_CREATED)
async def create_consent(
    data: ConsentRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Record user consent"""
    
    consent = ConsentRecord(
        id=str(uuid.uuid4()),
        tenant_id=user.tenant_id,
        user_id=user.id,
        scan_id=data.scan_id,
        consent_type=data.consent_type,
        consent_state=data.consent_state,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    
    db.add(consent)
    await db.commit()
    await db.refresh(consent)
    
    return ConsentResponse(
        id=consent.id,
        consent_type=consent.consent_type,
        consent_state=consent.consent_state,
        created_at=consent.created_at,
        revoked_at=consent.revoked_at,
    )


@router.get("/", response_model=list[ConsentResponse])
async def list_consents(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all consent records for current user"""
    
    result = await db.execute(
        select(ConsentRecord).where(
            ConsentRecord.user_id == user.id,
            ConsentRecord.tenant_id == user.tenant_id
        ).order_by(ConsentRecord.created_at.desc())
    )
    consents = result.scalars().all()
    
    return [
        ConsentResponse(
            id=consent.id,
            consent_type=consent.consent_type,
            consent_state=consent.consent_state,
            created_at=consent.created_at,
            revoked_at=consent.revoked_at,
        )
        for consent in consents
    ]


@router.patch("/{consent_id}/revoke", response_model=ConsentResponse)
async def revoke_consent(
    consent_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Revoke a consent record"""
    
    result = await db.execute(
        select(ConsentRecord).where(
            ConsentRecord.id == consent_id,
            ConsentRecord.user_id == user.id,
            ConsentRecord.tenant_id == user.tenant_id
        )
    )
    consent = result.scalar_one_or_none()
    
    if not consent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consent record not found"
        )
    
    consent.revoked_at = datetime.utcnow().isoformat()
    consent.consent_state = False
    
    await db.commit()
    await db.refresh(consent)
    
    return ConsentResponse(
        id=consent.id,
        consent_type=consent.consent_type,
        consent_state=consent.consent_state,
        created_at=consent.created_at,
        revoked_at=consent.revoked_at,
    )
