"""Create properties table.

Revision ID: 0001_create_properties
Revises: 0000_create_base
Create Date: 2026-08-27 00:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_create_properties"
down_revision = "0000_create_base"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create properties table
    op.create_table(
        "properties",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.String(500), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="UTC"),
        sa.Column("property_type", sa.String(100), nullable=False),
        sa.Column("units", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["portfolio_id"],
            ["portfolios.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Update devices table to reference properties instead of portfolios
    # Note: This assumes devices table exists. If not, skip this step.
    try:
        op.drop_constraint("devices_property_id_fkey", "devices", type_="foreignkey")
        op.create_foreign_key(
            "devices_property_id_fkey", "devices", "properties", ["property_id"], ["id"]
        )
    except Exception:
        # If the constraint doesn't exist, skip
        pass


def downgrade() -> None:
    # Downgrade: remove properties table
    op.drop_table("properties")

    # Restore original foreign key if needed
    try:
        op.drop_constraint("devices_property_id_fkey", "devices", type_="foreignkey")
        op.create_foreign_key(
            "devices_property_id_fkey", "devices", "portfolios", ["property_id"], ["id"]
        )
    except Exception:
        pass
