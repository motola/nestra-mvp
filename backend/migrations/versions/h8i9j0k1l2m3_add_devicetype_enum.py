"""Add devicetype enum for device classification.

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2m
Create Date: 2026-08-31

"""

from __future__ import annotations

from sqlalchemy.dialects.postgresql import ENUM

from alembic import op

revision = "h8i9j0k1l2m3"
down_revision = "g7h8i9j0k1l2m"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create devicetype enum
    devicetype_enum = ENUM(
        "lock",
        "thermostat",
        "camera",
        "plug",
        "sensor",
        "speaker",
        "light",
        name="devicetype",
    )
    devicetype_enum.create(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    op.execute("DROP TYPE IF EXISTS devicetype")
