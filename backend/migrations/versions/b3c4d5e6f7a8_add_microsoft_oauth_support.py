"""Add Microsoft OAuth support to users table

Revision ID: b3c4d5e6f7a8
Revises: a1b2c3d4e5f6
Create Date: 2026-08-17 00:15:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b3c4d5e6f7a8"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add microsoft_id column
    op.add_column(
        "users",
        sa.Column("microsoft_id", sa.String(255), nullable=True, unique=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "microsoft_id")
