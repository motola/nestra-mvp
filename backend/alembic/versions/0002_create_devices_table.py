"""Create devices table with enum types.

Revision ID: 0002_create_devices
Revises: 0001_create_properties
Create Date: 2026-08-31 00:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "0002_create_devices"
down_revision = "0001_create_properties"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create devicetype enum
    devicetype = postgresql.ENUM(
        "lock",
        "thermostat",
        "camera",
        "plug",
        "sensor",
        "speaker",
        "light",
        name="devicetype",
    )
    devicetype.create(op.get_bind(), checkfirst=True)

    # Create devices table
    op.create_table(
        "devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("integration_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "device_type",
            postgresql.ENUM(
                "lock",
                "thermostat",
                "camera",
                "plug",
                "sensor",
                "speaker",
                "light",
                name="devicetype",
            ),
            nullable=False,
        ),
        sa.Column("vendor", sa.String(255), nullable=False),
        sa.Column("vendor_specific_id", sa.String(255), nullable=False),
        sa.Column("vendor_name", sa.String(255), nullable=True),
        sa.Column("online", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_sync", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_state", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("manufacturer", sa.String(255), nullable=True),
        sa.Column("model", sa.String(255), nullable=True),
        sa.Column("serial_number", sa.String(255), nullable=True),
        sa.Column("ownership_type", sa.String(50), nullable=True),
        sa.Column("owner_property_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("owner_tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["portfolio_id"],
            ["portfolios.id"],
        ),
        sa.ForeignKeyConstraint(
            ["property_id"],
            ["properties.id"],
        ),
        sa.ForeignKeyConstraint(
            ["integration_id"],
            ["integrations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_property_id"],
            ["properties.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_devices_organization_id", "devices", ["organization_id"], unique=False)
    op.create_index("ix_devices_portfolio_id", "devices", ["portfolio_id"], unique=False)
    op.create_index("ix_devices_property_id", "devices", ["property_id"], unique=False)
    op.create_index("ix_devices_integration_id", "devices", ["integration_id"], unique=False)
    op.create_index("ix_devices_owner_property_id", "devices", ["owner_property_id"], unique=False)
    op.create_index(
        "idx_device_vendor_key", "devices", ["vendor", "vendor_specific_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("idx_device_vendor_key", table_name="devices")
    op.drop_index("ix_devices_owner_property_id", table_name="devices")
    op.drop_index("ix_devices_integration_id", table_name="devices")
    op.drop_index("ix_devices_property_id", table_name="devices")
    op.drop_index("ix_devices_portfolio_id", table_name="devices")
    op.drop_index("ix_devices_organization_id", table_name="devices")
    op.drop_table("devices")
    op.execute("DROP TYPE IF EXISTS devicetype")
