"""Add devices and integrations tables.

Revision ID: f5g6h7i8j9k0
Revises: e4f5a6b7c8d9
Create Date: 2026-08-28

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID as PGUUID

revision = "f5g6h7i8j9k0"
down_revision = "e4f5a6b7c8d9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "integrations",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("vendor", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_integrations_organization_id", "integrations", ["organization_id"])
    op.create_index("ix_integrations_vendor", "integrations", ["vendor"])

    op.create_table(
        "devices",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "property_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("properties.id"),
            nullable=False,
        ),
        sa.Column(
            "integration_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("integrations.id"),
            nullable=False,
        ),
        sa.Column("device_type", sa.String(50), nullable=False),
        sa.Column("vendor", sa.String(255), nullable=False),
        sa.Column("vendor_specific_id", sa.String(255), nullable=False),
        sa.Column("vendor_name", sa.String(255), nullable=True),
        sa.Column("online", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_sync", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_state", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_devices_organization_id", "devices", ["organization_id"])
    op.create_index("ix_devices_property_id", "devices", ["property_id"])
    op.create_index("ix_devices_integration_id", "devices", ["integration_id"])
    op.create_index("ix_devices_vendor", "devices", ["vendor"])
    op.create_index("ix_devices_vendor_specific_id", "devices", ["vendor_specific_id"])


def downgrade() -> None:
    op.drop_index("ix_devices_vendor_specific_id", table_name="devices")
    op.drop_index("ix_devices_vendor", table_name="devices")
    op.drop_index("ix_devices_integration_id", table_name="devices")
    op.drop_index("ix_devices_property_id", table_name="devices")
    op.drop_index("ix_devices_organization_id", table_name="devices")
    op.drop_table("devices")

    op.drop_index("ix_integrations_vendor", table_name="integrations")
    op.drop_index("ix_integrations_organization_id", table_name="integrations")
    op.drop_table("integrations")
