"""Add Google OAuth support to users table

Revision ID: 9c7d4e1a2b5f
Revises: 8f5e3a2c1b6d
Create Date: 2026-08-17 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "9c7d4e1a2b5f"
down_revision: str | Sequence[str] | None = "8f5e3a2c1b6d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make password_hash nullable
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(255),
        nullable=True,
    )

    # Add google_id column
    op.add_column(
        "users",
        sa.Column("google_id", sa.String(255), nullable=True, unique=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "google_id")

    # Make password_hash non-nullable again
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(255),
        nullable=False,
    )
