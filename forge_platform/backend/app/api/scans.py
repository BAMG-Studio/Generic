"""
Scan Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, Union
from ..db.session import get_db
from ..models.scan import Scan, Repository, ScanStatus
from ..models.user import User
from ..auth.dependencies import get_current_user, get_tenant_context
from ..services.scanner import scanner_service
import uuid
from datetime import datetime
import asyncio


def _format_timestamp(value: Optional[Union[datetime, str]]) -> Optional[str]:
    """Return ISO timestamp regardless of datetime or str input."""
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    return None

router = APIRouter(prefix="/scans", tags=["scans"])


class StartScanRequest(BaseModel):
    repository_id: str
    branch: Optional[str] = None
    commit_sha: Optional[str] = None
    scan_type: str = "full"


class ScanResponse(BaseModel):
    id: str
    repository_id: str
    status: str
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    total_files: int
    foreground_count: int
    third_party_count: int
    background_count: int
    
    class Config:
        from_attributes = True


@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def start_scan(
    data: StartScanRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Start a new repository scan"""
    
    # Verify repository exists and user has access
    result = await db.execute(
        select(Repository).where(
            Repository.id == data.repository_id,
            Repository.tenant_id == user.tenant_id
        )
    )
    repository = result.scalar_one_or_none()
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )
    
    # Create scan record
    scan = Scan(
        id=str(uuid.uuid4()),
        tenant_id=user.tenant_id,
        repository_id=data.repository_id,
        user_id=user.id,
        branch=data.branch or repository.default_branch,
        commit_sha=data.commit_sha,
        scan_type=data.scan_type,
        status=ScanStatus.QUEUED,
    )
    
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    
    # Queue background scan job
    background_tasks.add_task(
        process_scan_task,
        scan.id,
        repository.clone_url,
        data.branch or repository.default_branch,
        data.commit_sha
    )
    
    return ScanResponse(
        id=scan.id,
        repository_id=scan.repository_id,
        status=scan.status.value,
        created_at=_format_timestamp(scan.created_at),
        started_at=_format_timestamp(scan.started_at),
        completed_at=_format_timestamp(scan.completed_at),
        total_files=scan.total_files,
        foreground_count=scan.foreground_count,
        third_party_count=scan.third_party_count,
        background_count=scan.background_count,
    )


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get scan details"""
    
    result = await db.execute(
        select(Scan).where(
            Scan.id == scan_id,
            Scan.tenant_id == user.tenant_id
        )
    )
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    return ScanResponse(
        id=scan.id,
        repository_id=scan.repository_id,
        status=scan.status.value,
        created_at=_format_timestamp(scan.created_at),
        started_at=_format_timestamp(scan.started_at),
        completed_at=_format_timestamp(scan.completed_at),
        total_files=scan.total_files,
        foreground_count=scan.foreground_count,
        third_party_count=scan.third_party_count,
        background_count=scan.background_count,
    )


@router.get("/", response_model=list[ScanResponse])
async def list_scans(
    repository_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List scans for current tenant"""
    
    query = select(Scan).where(Scan.tenant_id == user.tenant_id)
    
    if repository_id:
        query = query.where(Scan.repository_id == repository_id)
    
    query = query.limit(limit).offset(offset).order_by(Scan.created_at.desc())
    
    result = await db.execute(query)
    scans = result.scalars().all()
    
    return [
        ScanResponse(
            id=scan.id,
            repository_id=scan.repository_id,
            status=scan.status.value,
            created_at=_format_timestamp(scan.created_at),
            started_at=_format_timestamp(scan.started_at),
            completed_at=_format_timestamp(scan.completed_at),
            total_files=scan.total_files,
            foreground_count=scan.foreground_count,
            third_party_count=scan.third_party_count,
            background_count=scan.background_count,
        )
        for scan in scans
    ]


async def process_scan_task(
    scan_id: str,
    repository_url: str,
    branch: Optional[str],
    commit_sha: Optional[str]
):
    """Background task to process a scan"""
    from ..db.session import async_session_maker
    
    async with async_session_maker() as db:
        try:
            await scanner_service.execute_scan(
                scan_id=scan_id,
                repository_url=repository_url,
                commit_sha=commit_sha,
                branch=branch,
                db=db
            )
        except Exception as e:
            print(f"Scan {scan_id} failed: {e}")
            # Error already logged by scanner_service
