"""add_token_system_tables

Revision ID: 1234567890ab
Revises: ed547beeae23
Create Date: 2025-11-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1234567890ab'
down_revision = 'ed547beeae23'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create api_tokens table
    op.create_table(
        'api_tokens',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('token_prefix', sa.String(length=8), nullable=False),
        sa.Column('token_hash', sa.String(), nullable=False),
        sa.Column('scopes', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=True),
        sa.Column('tier', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by_ip', sa.String(), nullable=True),
        sa.Column('last_used_ip', sa.String(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_tokens_token_hash'), 'api_tokens', ['token_hash'], unique=False)
    op.create_index(op.f('ix_api_tokens_user_id'), 'api_tokens', ['user_id'], unique=False)
    op.create_index(op.f('ix_api_tokens_tenant_id'), 'api_tokens', ['tenant_id'], unique=False)

    # Create token_usage_events table
    op.create_table(
        'token_usage_events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('token_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('endpoint', sa.String(), nullable=False),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['token_id'], ['api_tokens.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_token_usage_events_token_id'), 'token_usage_events', ['token_id'], unique=False)
    op.create_index(op.f('ix_token_usage_events_user_id'), 'token_usage_events', ['user_id'], unique=False)
    op.create_index(op.f('ix_token_usage_events_timestamp'), 'token_usage_events', ['timestamp'], unique=False)

    # Create usage_aggregates table
    op.create_table(
        'usage_aggregates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('token_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('request_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('success_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_response_time_ms', sa.Float(), nullable=True),
        sa.Column('endpoints_used', postgresql.JSONB(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['token_id'], ['api_tokens.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_usage_aggregates_token_id'), 'usage_aggregates', ['token_id'], unique=False)
    op.create_index(op.f('ix_usage_aggregates_user_id'), 'usage_aggregates', ['user_id'], unique=False)
    op.create_index(op.f('ix_usage_aggregates_date'), 'usage_aggregates', ['date'], unique=False)
    op.create_index('ix_usage_aggregates_token_date', 'usage_aggregates', ['token_id', 'date'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_usage_aggregates_token_date', table_name='usage_aggregates')
    op.drop_index(op.f('ix_usage_aggregates_date'), table_name='usage_aggregates')
    op.drop_index(op.f('ix_usage_aggregates_user_id'), table_name='usage_aggregates')
    op.drop_index(op.f('ix_usage_aggregates_token_id'), table_name='usage_aggregates')
    op.drop_table('usage_aggregates')
    
    op.drop_index(op.f('ix_token_usage_events_timestamp'), table_name='token_usage_events')
    op.drop_index(op.f('ix_token_usage_events_user_id'), table_name='token_usage_events')
    op.drop_index(op.f('ix_token_usage_events_token_id'), table_name='token_usage_events')
    op.drop_table('token_usage_events')
    
    op.drop_index(op.f('ix_api_tokens_tenant_id'), table_name='api_tokens')
    op.drop_index(op.f('ix_api_tokens_user_id'), table_name='api_tokens')
    op.drop_index(op.f('ix_api_tokens_token_hash'), table_name='api_tokens')
    op.drop_table('api_tokens')
