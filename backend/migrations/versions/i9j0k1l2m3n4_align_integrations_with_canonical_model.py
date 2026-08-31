"""Align deployed integrations schema with the canonical ORM model.

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2026-08-31

This forward-only normalization is safe for both databases upgraded through
the original integration migration and fresh databases using the corrected
in-place migration.
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision = "i9j0k1l2m3n4"
down_revision = "h8i9j0k1l2m3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Normalize indexes and the config type without replacing the table."""
    op.alter_column(
        "integrations",
        "config",
        existing_type=sa.JSON(),
        type_=JSONB(),
        existing_nullable=False,
        postgresql_using="config::jsonb",
        server_default=sa.text("'{}'::jsonb"),
    )

    op.execute("DROP INDEX IF EXISTS ix_integrations_organization_id")
    op.execute("DROP INDEX IF EXISTS ix_integrations_provider_id")
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_integrations_connection
        ON integrations (organization_id, provider_id, connection_identifier)
        WHERE deleted_at IS NULL
        """
    )


def downgrade() -> None:
    """Keep the canonical schema; this normalization is intentionally irreversible."""
