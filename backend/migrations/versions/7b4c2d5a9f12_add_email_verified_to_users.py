"""Add email_verified column to users table

Revision ID: 7b4c2d5a9f12
Revises: 5a358f418431
Create Date: 2026-08-15 22:54:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "7b4c2d5a9f12"
down_revision: str | Sequence[str] | None = "5a358f418431"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "email_verified")
