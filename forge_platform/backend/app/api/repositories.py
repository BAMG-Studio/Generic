"""
Repository Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from ..db.session import get_db
from ..models.scan import Repository
from ..models.user import User
from ..auth.dependencies import get_current_user
import uuid

router = APIRouter(prefix="/repositories", tags=["repositories"])


class CreateRepositoryRequest(BaseModel):
    name: str
    full_name: str
    provider: str
    clone_url: str
    default_branch: str = "main"
    description: Optional[str] = None
    is_private: bool = False


class RepositoryResponse(BaseModel):
    id: str
    name: str
    full_name: str
    provider: str
    default_branch: str
    description: Optional[str]
    is_active: bool
    last_scanned_at: Optional[str]
    
    class Config:
        from_attributes = True


@router.post("/", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
async def create_repository(
    data: CreateRepositoryRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Connect a new repository"""
    
    # Check if repository already exists
    result = await db.execute(
        select(Repository).where(
            Repository.full_name == data.full_name,
            Repository.tenant_id == user.tenant_id
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Repository already connected"
        )
    
    repository = Repository(
        id=str(uuid.uuid4()),
        tenant_id=user.tenant_id,
        user_id=user.id,
        name=data.name,
        full_name=data.full_name,
        provider=data.provider,
        clone_url=data.clone_url,
        default_branch=data.default_branch,
        description=data.description,
        is_private=data.is_private,
    )
    
    db.add(repository)
    await db.commit()
    await db.refresh(repository)
    
    return RepositoryResponse(
        id=repository.id,
        name=repository.name,
        full_name=repository.full_name,
        provider=repository.provider,
        default_branch=repository.default_branch,
        description=repository.description,
        is_active=repository.is_active,
        last_scanned_at=repository.last_scanned_at,
    )


@router.get("/", response_model=list[RepositoryResponse])
async def list_repositories(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all repositories for current tenant"""
    
    result = await db.execute(
        select(Repository).where(
            Repository.tenant_id == user.tenant_id,
            Repository.is_active == True
        ).order_by(Repository.created_at.desc())
    )
    repositories = result.scalars().all()
    
    return [
        RepositoryResponse(
            id=repo.id,
            name=repo.name,
            full_name=repo.full_name,
            provider=repo.provider,
            default_branch=repo.default_branch,
            description=repo.description,
            is_active=repo.is_active,
            last_scanned_at=repo.last_scanned_at,
        )
        for repo in repositories
    ]


@router.get("/{repository_id}", response_model=RepositoryResponse)
async def get_repository(
    repository_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get repository details"""
    
    result = await db.execute(
        select(Repository).where(
            Repository.id == repository_id,
            Repository.tenant_id == user.tenant_id
        )
    )
    repository = result.scalar_one_or_none()
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )
    
    return RepositoryResponse(
        id=repository.id,
        name=repository.name,
        full_name=repository.full_name,
        provider=repository.provider,
        default_branch=repository.default_branch,
        description=repository.description,
        is_active=repository.is_active,
        last_scanned_at=repository.last_scanned_at,
    )
