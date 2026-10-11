"""Add Microsoft OAuth support to users table

Revision ID: b3c4d5e6f7a8
Revises: c2d3e4f5a6b7
Create Date: 2026-08-17 00:15:00.000000

"""

from collections.abc import Sequence

revision: str = "b3c4d5e6f7a8"
down_revision: str | Sequence[str] | None = "c2d3e4f5a6b7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Note: microsoft_id column was added in a1b2c3d4e5f6
    # This migration serves as a merge point for parallel branches
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
