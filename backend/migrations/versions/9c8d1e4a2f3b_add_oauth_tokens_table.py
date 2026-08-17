"""Add oauth_tokens table for device integrations.

Revision ID: 9c8d1e4a2f3b
Revises: 8f5e3a2c1b6d
Create Date: 2026-08-17 12:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "9c8d1e4a2f3b"
down_revision = "8f5e3a2c1b6d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create oauth_tokens table."""
    op.create_table(
        "oauth_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vendor", sa.String(50), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("token_type", sa.String(20), nullable=False, server_default="Bearer"),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_response", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_oauth_tokens_organization_id",
        "oauth_tokens",
        ["organization_id"],
    )
    op.create_index(
        "ix_oauth_tokens_vendor",
        "oauth_tokens",
        ["vendor"],
    )


def downgrade() -> None:
    """Drop oauth_tokens table."""
    op.drop_index("ix_oauth_tokens_vendor", table_name="oauth_tokens")
    op.drop_index("ix_oauth_tokens_organization_id", table_name="oauth_tokens")
    op.drop_table("oauth_tokens")
