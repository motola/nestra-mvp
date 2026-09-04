"""Add indexes used by audit event queries.

Revision ID: k1l2m3n4o5p6
Revises: j0k1l2m3n4o5
Create Date: 2026-09-01
"""

from __future__ import annotations

from alembic import op

revision = "k1l2m3n4o5p6"
down_revision = "j0k1l2m3n4o5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the indexes declared by AuditEventModel."""
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_audit_events_resource_type ON audit_events (resource_type)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_audit_events_resource_id ON audit_events (resource_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_audit_org_action_created "
        "ON audit_events (organization_id, action, created_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_audit_resource_created "
        "ON audit_events (resource_type, resource_id, created_at)"
    )


def downgrade() -> None:
    """Drop audit query indexes added by this revision."""
    op.execute("DROP INDEX IF EXISTS idx_audit_resource_created")
    op.execute("DROP INDEX IF EXISTS idx_audit_org_action_created")
    op.execute("DROP INDEX IF EXISTS ix_audit_events_resource_id")
    op.execute("DROP INDEX IF EXISTS ix_audit_events_resource_type")
