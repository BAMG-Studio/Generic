"""
Scan and Repository Models
"""
from sqlalchemy import Column, String, JSON, Boolean, Integer, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from ..db.base import Base
import enum


class ScanStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Repository(Base):
    """Connected repository"""
    __tablename__ = "repositories"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Repository details
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)  # org/repo
    provider = Column(String, nullable=False)  # github, gitlab, bitbucket
    clone_url = Column(String, nullable=False)
    default_branch = Column(String, default="main")
    
    # Repository metadata
    description = Column(Text, nullable=True)
    language = Column(String, nullable=True)
    stars = Column(Integer, default=0)
    is_private = Column(Boolean, default=False)
    
    # Scan configuration
    auto_scan_on_push = Column(Boolean, default=False)
    scan_schedule = Column(String, nullable=True)  # cron expression
    
    # Status
    is_active = Column(Boolean, default=True)
    last_scanned_at = Column(String, nullable=True)
    
    # External ID from provider
    external_id = Column(String, nullable=True)


class Scan(Base):
    """Audit scan execution"""
    __tablename__ = "scans"
    
    repository_id = Column(String, ForeignKey("repositories.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Scan configuration
    commit_sha = Column(String, nullable=True)
    branch = Column(String, nullable=True)
    scan_type = Column(String, default="full")  # full, incremental, targeted
    
    # Execution
    status = Column(SQLEnum(ScanStatus), default=ScanStatus.QUEUED, nullable=False)
    started_at = Column(String, nullable=True)
    completed_at = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # ML Model
    model_version = Column(String, nullable=True)
    model_id = Column(String, nullable=True)
    
    # Results summary
    total_files = Column(Integer, default=0)
    foreground_count = Column(Integer, default=0)
    third_party_count = Column(Integer, default=0)
    background_count = Column(Integer, default=0)
    
    # Findings summary
    critical_issues = Column(Integer, default=0)
    high_issues = Column(Integer, default=0)
    medium_issues = Column(Integer, default=0)
    low_issues = Column(Integer, default=0)
    
    # Detailed results (stored in S3/object storage)
    results_url = Column(String, nullable=True)
    report_url = Column(String, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)
    
    # Additional data
    scan_metadata = Column(JSON, default={})


class ConsentRecord(Base):
    """User consent for ML training and data retention"""
    __tablename__ = "consent_records"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    scan_id = Column(String, ForeignKey("scans.id"), nullable=True)
    
    # Consent types
    consent_type = Column(String, nullable=False)  # ML_DATA_USE, LONG_TERM_RETENTION, ANALYTICS, MARKETING
    consent_state = Column(Boolean, nullable=False)
    
    # Context
    consent_text = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Revocation
    revoked_at = Column(String, nullable=True)
    revocation_reason = Column(Text, nullable=True)


class AuditLog(Base):
    """Immutable audit trail"""
    __tablename__ = "audit_logs"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Event details
    event_type = Column(String, nullable=False)  # login, scan_start, export, etc
    resource_type = Column(String, nullable=True)  # scan, repository, user
    resource_id = Column(String, nullable=True)
    
    # Action details
    action = Column(String, nullable=False)
    status = Column(String, nullable=False)  # success, failure
    
    # Context
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    details = Column(JSON, default={})
    
    # Cryptographic integrity
    signature = Column(String, nullable=True)
