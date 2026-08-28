"""Add auth tokens tables for password reset and email verification

Revision ID: 5a358f418431
Revises: 4702fb9fbefc
Create Date: 2026-08-15 22:53:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from alembic import op

revision: str = "5a358f418431"
down_revision: str | Sequence[str] | None = "4702fb9fbefc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create password_reset_tokens table
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("token", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token", name="uq_password_reset_token"),
    )

    # Create email_verification_tokens table
    op.create_table(
        "email_verification_tokens",
        sa.Column("id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("token", sa.String(255), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token", name="uq_email_verification_token"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("email_verification_tokens")
    op.drop_table("password_reset_tokens")
