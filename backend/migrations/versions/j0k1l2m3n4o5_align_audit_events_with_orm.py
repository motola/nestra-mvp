"""Align audit events with the canonical ORM model.

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
Create Date: 2026-08-31

The deployed audit table used legacy ``metadata`` and ``occurred_at`` names.
This migration preserves existing rows and updates the table in place.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "j0k1l2m3n4o5"
down_revision = "i9j0k1l2m3n4"
branch_labels = None
depends_on = None


def _column_names() -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns("audit_events")}


def upgrade() -> None:
    """Rename legacy columns and add fields required by AuditEventModel."""
    columns = _column_names()

    if "metadata" in columns and "changes" not in columns:
        op.alter_column("audit_events", "metadata", new_column_name="changes")
    elif "changes" not in columns:
        op.add_column(
            "audit_events",
            sa.Column("changes", JSONB(), nullable=True),
        )

    columns = _column_names()
    if "occurred_at" in columns and "created_at" not in columns:
        op.alter_column("audit_events", "occurred_at", new_column_name="created_at")
    elif "created_at" not in columns:
        op.add_column(
            "audit_events",
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )

    columns = _column_names()
    additions = (
        sa.Column("resource_name", sa.String(500), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="success"),
        sa.Column("reason", sa.String(1000), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
    )
    for column in additions:
        if column.name not in columns:
            op.add_column("audit_events", column)

    op.execute("UPDATE audit_events SET changes = '{}'::jsonb WHERE changes IS NULL")
    op.alter_column(
        "audit_events",
        "changes",
        existing_type=JSONB(),
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
    )

    op.execute("DROP INDEX IF EXISTS ix_audit_events_occurred")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_events_created_at ON audit_events (created_at)")


def downgrade() -> None:
    """Keep the canonical audit schema to avoid destructive data loss."""
