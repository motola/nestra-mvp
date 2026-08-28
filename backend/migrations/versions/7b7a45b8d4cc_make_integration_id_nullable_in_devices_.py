"""make integration_id nullable in devices table

Revision ID: 7b7a45b8d4cc
Revises: f5g6h7i8j9k0
Create Date: 2026-08-28 16:53:42.554753

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7b7a45b8d4cc"
down_revision: str | Sequence[str] | None = "f5g6h7i8j9k0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "devices",
        "integration_id",
        existing_type=sa.UUID(),
        nullable=True,
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "devices",
        "integration_id",
        existing_type=sa.UUID(),
        nullable=False,
        existing_nullable=True,
    )
