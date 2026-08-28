"""Add properties table.

Revision ID: e4f5a6b7c8d9
Revises: None
Create Date: 2026-08-28

"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from alembic import op

revision = "e4f5a6b7c8d9"
down_revision = "d3e4f5a6b7c8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "properties",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "portfolio_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("portfolios.id"),
            nullable=False,
        ),
        sa.Column("organization_id", PGUUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.String(500), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="UTC"),
        sa.Column("property_type", sa.String(100), nullable=False),
        sa.Column("units", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_properties_portfolio_id", "properties", ["portfolio_id"])
    op.create_index("ix_properties_organization_id", "properties", ["organization_id"])


def downgrade() -> None:
    op.drop_index("ix_properties_organization_id", table_name="properties")
    op.drop_index("ix_properties_portfolio_id", table_name="properties")
    op.drop_table("properties")
