"""Add revoked_tokens table for logout token revocation

Revision ID: a1b2c3d4e5f6
Revises: 9c7d4e1a2b5f
Create Date: 2026-08-17 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "9c7d4e1a2b5f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS revoked_tokens (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id),
            token_jti VARCHAR(255) NOT NULL UNIQUE,
            revoked_at TIMESTAMP WITH TIME ZONE NOT NULL,
            expires_at TIMESTAMP WITH TIME ZONE NOT NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_revoked_tokens_expires_at ON revoked_tokens(expires_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_revoked_tokens_token_jti ON revoked_tokens(token_jti)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("revoked_tokens")
