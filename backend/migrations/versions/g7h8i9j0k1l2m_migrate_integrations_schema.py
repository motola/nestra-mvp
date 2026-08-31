"""Migrate integrations to the provider-based schema in place.

Revision ID: g7h8i9j0k1l2m
Revises: g7h8i9j0k1l2
Create Date: 2026-08-31

Existing integration IDs are preserved so devices, device integrations, and
commands retain valid foreign-key references.
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from alembic import op

revision = "g7h8i9j0k1l2m"
down_revision = "g7h8i9j0k1l2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Convert integrations from vendor UUIDs to provider slugs in place."""
    op.execute("DROP INDEX IF EXISTS uq_integrations_connection")
    op.execute("DROP INDEX IF EXISTS ix_integrations_provider_id")
    op.execute("DROP INDEX IF EXISTS ix_integrations_organization_id")
    op.execute("ALTER TABLE integrations DROP CONSTRAINT IF EXISTS integrations_provider_id_fkey")

    op.add_column(
        "integrations",
        sa.Column("provider_slug", sa.String(50), nullable=True),
    )
    op.execute(
        """
        UPDATE integrations AS integration
        SET provider_slug = COALESCE(
            (
                SELECT provider.slug
                FROM providers AS provider
                WHERE provider.id = integration.provider_id
            ),
            NULLIF(
                LOWER(REGEXP_REPLACE(integration.vendor, '[^a-zA-Z0-9]+', '_', 'g')),
                ''
            ),
            'unknown'
        )
        """
    )
    op.alter_column(
        "integrations",
        "provider_slug",
        existing_type=sa.String(50),
        nullable=False,
    )
    op.drop_column("integrations", "provider_id")
    op.alter_column("integrations", "provider_slug", new_column_name="provider_id")

    op.add_column(
        "integrations",
        sa.Column(
            "account_identifier",
            sa.String(255),
            nullable=False,
            server_default="",
        ),
    )
    op.add_column(
        "integrations",
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.execute(
        "UPDATE integrations SET enabled = CASE WHEN status = 'ACTIVE' THEN TRUE ELSE FALSE END"
    )

    op.alter_column(
        "integrations",
        "connection_identifier",
        existing_type=sa.String(255),
        type_=sa.String(500),
        existing_nullable=True,
    )
    op.execute("UPDATE integrations SET config = '{}'::jsonb WHERE config IS NULL")
    op.alter_column(
        "integrations",
        "config",
        existing_type=JSONB(),
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
    )

    op.drop_column("integrations", "vendor")
    op.drop_column("integrations", "status")

    op.create_index("idx_integration_provider", "integrations", ["provider_id"])
    op.create_index("idx_integration_org", "integrations", ["organization_id"])
    op.execute(
        """
        CREATE UNIQUE INDEX uq_integrations_connection
        ON integrations (organization_id, provider_id, connection_identifier)
        WHERE deleted_at IS NULL
        """
    )


def downgrade() -> None:
    """Restore the UUID-provider schema used by the preceding revision."""
    op.execute("DROP INDEX IF EXISTS uq_integrations_connection")
    op.execute("DROP INDEX IF EXISTS idx_integration_provider")
    op.execute("DROP INDEX IF EXISTS idx_integration_org")

    op.add_column(
        "integrations",
        sa.Column("vendor", sa.String(255), nullable=True),
    )
    op.add_column(
        "integrations",
        sa.Column("status", sa.String(50), nullable=True),
    )
    op.execute("UPDATE integrations SET vendor = provider_id")
    op.execute(
        "UPDATE integrations SET status = CASE WHEN enabled THEN 'ACTIVE' ELSE 'DISABLED' END"
    )
    op.alter_column("integrations", "vendor", nullable=False)
    op.alter_column("integrations", "status", nullable=False, server_default="ACTIVE")

    op.add_column(
        "integrations",
        sa.Column("provider_uuid", PGUUID(as_uuid=True), nullable=True),
    )
    op.execute(
        """
        UPDATE integrations AS integration
        SET provider_uuid = (
            SELECT provider.id
            FROM providers AS provider
            WHERE provider.slug = integration.provider_id
            LIMIT 1
        )
        """
    )
    op.drop_column("integrations", "provider_id")
    op.alter_column("integrations", "provider_uuid", new_column_name="provider_id")
    op.create_foreign_key(
        "integrations_provider_id_fkey",
        "integrations",
        "providers",
        ["provider_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.alter_column(
        "integrations",
        "connection_identifier",
        existing_type=sa.String(500),
        type_=sa.String(255),
        existing_nullable=True,
    )
    op.alter_column(
        "integrations",
        "config",
        existing_type=JSONB(),
        nullable=True,
        server_default=None,
    )
    op.drop_column("integrations", "enabled")
    op.drop_column("integrations", "account_identifier")

    op.create_index("ix_integrations_provider_id", "integrations", ["provider_id"])
    op.create_index(
        "ix_integrations_organization_id",
        "integrations",
        ["organization_id"],
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_integrations_connection
        ON integrations (organization_id, provider_id, connection_identifier)
        WHERE provider_id IS NOT NULL AND deleted_at IS NULL
        """
    )
