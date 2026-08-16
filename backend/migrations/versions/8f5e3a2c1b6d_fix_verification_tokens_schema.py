"""Fix verification tokens schema to match model

Revision ID: 8f5e3a2c1b6d
Revises: 7b4c2d5a9f12
Create Date: 2026-08-16 20:40:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision: str = "8f5e3a2c1b6d"
down_revision: str | Sequence[str] | None = "7b4c2d5a9f12"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create token_type enum
    op.execute("CREATE TYPE token_type AS ENUM ('EMAIL_VERIFICATION', 'PASSWORD_RESET')")

    # Create verification_tokens table with correct schema
    op.create_table(
        "verification_tokens",
        sa.Column("id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("token", sa.String(255), nullable=False),
        sa.Column(
            "token_type",
            sa.Enum("EMAIL_VERIFICATION", "PASSWORD_RESET", name="token_type"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token", name="uq_verification_token"),
    )

    # Drop old tables if they exist
    op.execute("DROP TABLE IF EXISTS email_verification_tokens CASCADE")
    op.execute("DROP TABLE IF EXISTS password_reset_tokens CASCADE")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("verification_tokens")
    op.execute("DROP TYPE IF EXISTS token_type")
