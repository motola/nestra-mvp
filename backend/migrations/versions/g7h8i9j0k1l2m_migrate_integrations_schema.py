"""Migrate integrations table to new schema.

Revision ID: g7h8i9j0k1l2m
Revises: g7h8i9j0k1l2
Create Date: 2026-08-31

"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from alembic import op

revision = "g7h8i9j0k1l2m"
down_revision = "g7h8i9j0k1l2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop foreign key constraints that depend on integrations table
    op.drop_constraint("devices_integration_id_fkey", "devices", type_="foreignkey")
    op.drop_constraint(
        "device_integrations_integration_id_fkey", "device_integrations", type_="foreignkey"
    )
    op.drop_constraint("commands_integration_id_fkey", "commands", type_="foreignkey")

    # Drop old integrations table
    op.drop_index("ix_integrations_vendor", table_name="integrations")
    op.drop_index("ix_integrations_organization_id", table_name="integrations")
    op.drop_table("integrations")

    # Create new integrations table with correct schema
    op.create_table(
        "integrations",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("provider_id", sa.String(50), nullable=False, index=True),
        sa.Column("account_identifier", sa.String(255), nullable=False, server_default=""),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("connection_identifier", sa.String(500), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("credential_provider", sa.String(100), nullable=True),
        sa.Column("credential_ref", sa.String(500), nullable=True),
        sa.Column("oauth_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("config", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Create indexes
    op.create_index("idx_integration_provider", "integrations", ["provider_id"])
    op.create_index("idx_integration_org", "integrations", ["organization_id"])

    # Recreate foreign key constraints
    op.create_foreign_key(
        "devices_integration_id_fkey", "devices", "integrations", ["integration_id"], ["id"]
    )
    op.create_foreign_key(
        "device_integrations_integration_id_fkey",
        "device_integrations",
        "integrations",
        ["integration_id"],
        ["id"],
    )
    op.create_foreign_key(
        "commands_integration_id_fkey", "commands", "integrations", ["integration_id"], ["id"]
    )


def downgrade() -> None:
    # Drop foreign key constraints
    op.drop_constraint("devices_integration_id_fkey", "devices", type_="foreignkey")
    op.drop_constraint(
        "device_integrations_integration_id_fkey", "device_integrations", type_="foreignkey"
    )
    op.drop_constraint("commands_integration_id_fkey", "commands", type_="foreignkey")

    # Drop new integrations table
    op.drop_index("idx_integration_org", table_name="integrations")
    op.drop_index("idx_integration_provider", table_name="integrations")
    op.drop_table("integrations")

    # Restore old integrations table
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
