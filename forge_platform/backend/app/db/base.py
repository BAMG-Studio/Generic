"""
SQLAlchemy Base Models with Multi-Tenant Support
"""
from datetime import datetime
from typing import Any
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.orm import DeclarativeBase
import uuid


class Base(DeclarativeBase):
    """Base model with common fields and multi-tenant support"""
    
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Multi-tenancy (every record belongs to a tenant)
    tenant_id = Column(String, index=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    
    def dict(self) -> dict[str, Any]:
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
