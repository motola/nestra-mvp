"""Add audit and device enums required for audit logging and device management.

Revision ID: h9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2026-08-31

"""

from __future__ import annotations

from alembic import op
from sqlalchemy.dialects.postgresql import ENUM

revision = "h9j0k1l2m3n4"
down_revision = "h8i9j0k1l2m3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create auditactortype enum
    auditactortype_enum = ENUM(
        "user",
        "system",
        "automation",
        name="auditactortype",
    )
    auditactortype_enum.create(op.get_bind(), checkfirst=True)

    # Create auditaction enum
    auditaction_enum = ENUM(
        "device_created",
        "device_updated",
        "device_deleted",
        "command_executed",
        "command_failed",
        "access_granted",
        "access_revoked",
        "share_link_created",
        name="auditaction",
    )
    auditaction_enum.create(op.get_bind(), checkfirst=True)

    # Create auditresourcetype enum
    auditresourcetype_enum = ENUM(
        "device",
        "property",
        "command",
        "grant",
        "access_grant",
        "share_link",
        name="auditresourcetype",
    )
    auditresourcetype_enum.create(op.get_bind(), checkfirst=True)

    # Create auditstatus enum
    auditstatus_enum = ENUM(
        "success",
        "failure",
        name="auditstatus",
    )
    auditstatus_enum.create(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    op.execute("DROP TYPE IF EXISTS auditstatus")
    op.execute("DROP TYPE IF EXISTS auditresourcetype")
    op.execute("DROP TYPE IF EXISTS auditaction")
    op.execute("DROP TYPE IF EXISTS auditactortype")
