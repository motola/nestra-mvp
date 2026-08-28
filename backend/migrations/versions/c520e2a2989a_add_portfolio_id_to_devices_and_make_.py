"""add portfolio_id to devices and make integration_id required

Revision ID: c520e2a2989a
Revises: f5g6h7i8j9k0
Create Date: 2026-08-28 20:46:32.421012

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c520e2a2989a"
down_revision: str | Sequence[str] | None = "f5g6h7i8j9k0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "devices",
        sa.Column("portfolio_id", sa.UUID(), nullable=True),
    )

    # Backfill existing devices: assign to first portfolio per organization
    # This assumes each organization has at least one portfolio
    op.execute(
        """
        UPDATE devices d
        SET portfolio_id = (
            SELECT id FROM portfolios
            WHERE organization_id = d.organization_id
            ORDER BY created_at ASC
            LIMIT 1
        )
        WHERE d.portfolio_id IS NULL
        """
    )

    op.create_foreign_key(
        "fk_devices_portfolio_id",
        "devices",
        "portfolios",
        ["portfolio_id"],
        ["id"],
    )
    op.create_index("ix_devices_portfolio_id", "devices", ["portfolio_id"])

    # Make portfolio_id NOT NULL after backfill
    op.alter_column(
        "devices",
        "portfolio_id",
        existing_type=sa.UUID(),
        nullable=False,
        existing_nullable=True,
    )

    op.alter_column(
        "devices",
        "integration_id",
        existing_type=sa.UUID(),
        nullable=False,
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_devices_portfolio_id", table_name="devices")
    op.drop_constraint("fk_devices_portfolio_id", "devices", type_="foreignkey")
    op.drop_column("devices", "portfolio_id")

    op.alter_column(
        "devices",
        "integration_id",
        existing_type=sa.UUID(),
        nullable=True,
        existing_nullable=False,
    )
