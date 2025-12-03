"""
Role-Based Access Control Models
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from ..db.base import Base
from enum import Enum


class Permission(str, Enum):
    """Granular permissions for RBAC"""
    # Audit permissions
    READ_OWN_AUDITS = "read:own_audits"
    READ_ALL_AUDITS = "read:all_audits"
    WRITE_AUDITS = "write:audits"
    DELETE_AUDITS = "delete:audits"
    
    # Report permissions
    READ_REPORTS = "read:reports"
    GENERATE_REPORTS = "generate:reports"
    EXPORT_REPORTS = "export:reports"
    
    # Token permissions
    READ_OWN_TOKENS = "read:own_tokens"
    READ_ALL_TOKENS = "read:all_tokens"
    WRITE_TOKENS = "write:tokens"
    REVOKE_TOKENS = "revoke:tokens"
    
    # User permissions
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    DELETE_USERS = "delete:users"
    
    # Tenant permissions
    READ_TENANT = "read:tenant"
    WRITE_TENANT = "write:tenant"
    READ_ALL_TENANTS = "read:all_tenants"
    WRITE_ALL_TENANTS = "write:all_tenants"
    
    # Webhook permissions
    READ_WEBHOOKS = "read:webhooks"
    WRITE_WEBHOOKS = "write:webhooks"
    
    # Admin permissions
    ADMIN_SETTINGS = "admin:settings"
    ADMIN_BILLING = "admin:billing"
    ADMIN_ANALYTICS = "admin:analytics"


# Role-Permission mapping
ROLE_PERMISSIONS = {
    "super_admin": [p.value for p in Permission],  # All permissions
    
    "tenant_admin": [
        Permission.READ_ALL_AUDITS,
        Permission.WRITE_AUDITS,
        Permission.DELETE_AUDITS,
        Permission.READ_REPORTS,
        Permission.GENERATE_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.READ_ALL_TOKENS,
        Permission.WRITE_TOKENS,
        Permission.REVOKE_TOKENS,
        Permission.READ_USERS,
        Permission.WRITE_USERS,
        Permission.DELETE_USERS,
        Permission.READ_TENANT,
        Permission.WRITE_TENANT,
        Permission.READ_WEBHOOKS,
        Permission.WRITE_WEBHOOKS,
        Permission.ADMIN_BILLING,
    ],
    
    "user": [
        Permission.READ_OWN_AUDITS,
        Permission.WRITE_AUDITS,
        Permission.READ_REPORTS,
        Permission.GENERATE_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.READ_OWN_TOKENS,
        Permission.WRITE_TOKENS,
        Permission.READ_TENANT,
    ],
    
    "viewer": [
        Permission.READ_OWN_AUDITS,
        Permission.READ_REPORTS,
        Permission.EXPORT_REPORTS,
    ],
}


# Token tier scopes
TOKEN_TIER_SCOPES = {
    "free": [
        "read:reports",
        "read:audits",
    ],
    
    "professional": [
        "read:reports",
        "read:audits",
        "write:audits",
        "read:webhooks",
        "write:webhooks",
    ],
    
    "enterprise": [
        "read:*",
        "write:*",
        "admin:tenant",
    ],
}


def has_permission(user_role: str, permission: Permission) -> bool:
    """Check if a role has a specific permission"""
    return permission.value in ROLE_PERMISSIONS.get(user_role, [])


def has_scope(token_scopes: str, required_scope: str) -> bool:
    """Check if token has required scope"""
    scopes = [s.strip() for s in token_scopes.split(",")]
    
    # Check for wildcard scopes
    if required_scope in scopes:
        return True
    
    # Check for wildcard patterns (e.g., read:* matches read:audits)
    for scope in scopes:
        if scope.endswith(":*"):
            prefix = scope[:-1]  # Remove *
            if required_scope.startswith(prefix):
                return True
    
    return False
