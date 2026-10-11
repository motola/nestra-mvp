"""Fix verification tokens schema to match model

Revision ID: 8f5e3a2c1b6d
Revises: 7b4c2d5a9f12
Create Date: 2026-08-16 20:40:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "8f5e3a2c1b6d"
down_revision: str | Sequence[str] | None = "7b4c2d5a9f12"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop old tables if they exist
    op.execute("DROP TABLE IF EXISTS email_verification_tokens CASCADE")
    op.execute("DROP TABLE IF EXISTS password_reset_tokens CASCADE")

    # Create or verify token_type enum exists
    op.execute(
        "DO $$ BEGIN IF NOT EXISTS "
        "(SELECT 1 FROM pg_type WHERE typname = 'token_type') "
        "THEN CREATE TYPE token_type AS ENUM "
        "('EMAIL_VERIFICATION', 'PASSWORD_RESET'); END IF; END $$"
    )

    # Check if verification_tokens already exists
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS verification_tokens (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id),
            token VARCHAR(255) NOT NULL UNIQUE,
            token_type token_type NOT NULL,
            expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL,
            used_at TIMESTAMP WITH TIME ZONE
        )
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("verification_tokens")
    op.execute("DROP TYPE IF EXISTS token_type")
