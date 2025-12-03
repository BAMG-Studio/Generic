#!/usr/bin/env python3
"""
ForgeTrace Control Center CLI
Manage users, tokens, and tenants
"""
import asyncio
import sys
from sqlalchemy import select
import bcrypt
import click

from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole, Tenant, TenantTier
from app.models.token import APIToken


@click.group()
def cli():
    """ForgeTrace Control Center CLI"""
    pass


@cli.command()
@click.option('--email', prompt=True, help='User email')
@click.option('--password', prompt=True, hide_input=True, help='User password')
@click.option('--name', prompt=True, help='Full name')
@click.option('--role', type=click.Choice(['super_admin', 'tenant_admin', 'user', 'viewer']), default='user')
def create_user(email, password, name, role):
    """Create a new user"""
    async def _create():
        async with AsyncSessionLocal() as db:
            # Check if user exists
            result = await db.execute(select(User).where(User.email == email))
            if result.scalar_one_or_none():
                click.echo(f"❌ User {email} already exists")
                return
            
            # Create tenant
            tenant = Tenant(
                name=f"{name}'s Organization",
                slug=email.split('@')[0],
                tier=TenantTier.FREE
            )
            db.add(tenant)
            await db.flush()
            
            # Hash password
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            
            # Create user
            user = User(
                email=email,
                hashed_password=hashed,
                full_name=name,
                role=UserRole(role),
                tenant_id=tenant.id,
                is_active=True,
                is_verified=True
            )
            db.add(user)
            await db.commit()
            
            click.echo(f"✓ User created: {email} ({role})")
    
    asyncio.run(_create())


@cli.command()
@click.option('--email', prompt=True, help='User email')
def create_token(email):
    """Create API token for user"""
    async def _create():
        async with AsyncSessionLocal() as db:
            # Find user
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            
            if not user:
                click.echo(f"❌ User {email} not found")
                return
            
            # Generate token
            full_token, prefix, hashed = APIToken.generate_token()
            
            # Create token
            token = APIToken(
                user_id=user.id,
                tenant_id=user.tenant_id,
                name="CLI Generated Token",
                token_prefix=prefix,
                hashed_token=hashed,
                scopes="read:audits,write:audits,read:reports",
                is_active=True
            )
            db.add(token)
            await db.commit()
            
            click.echo(f"✓ Token created for {email}")
            click.echo(f"Token: {full_token}")
            click.echo(f"⚠️  Save this token - it won't be shown again!")
    
    asyncio.run(_create())


@cli.command()
def list_users():
    """List all users"""
    async def _list():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
            
            if not users:
                click.echo("No users found")
                return
            
            click.echo(f"\n{'Email':<30} {'Name':<25} {'Role':<15} {'Active'}")
            click.echo("-" * 80)
            for user in users:
                click.echo(f"{user.email:<30} {user.full_name:<25} {user.role.value:<15} {'✓' if user.is_active else '✗'}")
    
    asyncio.run(_list())


@cli.command()
@click.option('--email', prompt=True, help='User email')
def list_tokens(email):
    """List tokens for user"""
    async def _list():
        async with AsyncSessionLocal() as db:
            # Find user
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            
            if not user:
                click.echo(f"❌ User {email} not found")
                return
            
            # Get tokens
            result = await db.execute(select(APIToken).where(APIToken.user_id == user.id))
            tokens = result.scalars().all()
            
            if not tokens:
                click.echo(f"No tokens found for {email}")
                return
            
            click.echo(f"\n{'Prefix':<15} {'Name':<25} {'Scopes':<30} {'Active'}")
            click.echo("-" * 80)
            for token in tokens:
                click.echo(f"{token.token_prefix:<15} {token.name:<25} {token.scopes:<30} {'✓' if token.is_active else '✗'}")
    
    asyncio.run(_list())


@cli.command()
@click.option('--prefix', prompt=True, help='Token prefix (ftk_xxxxxxxx)')
def revoke_token(prefix):
    """Revoke an API token"""
    async def _revoke():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(APIToken).where(APIToken.token_prefix == prefix))
            token = result.scalar_one_or_none()
            
            if not token:
                click.echo(f"❌ Token {prefix} not found")
                return
            
            token.is_active = False
            await db.commit()
            
            click.echo(f"✓ Token {prefix} revoked")
    
    asyncio.run(_revoke())


if __name__ == '__main__':
    cli()
