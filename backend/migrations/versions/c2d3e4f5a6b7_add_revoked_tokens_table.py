"""Add revoked_tokens table for logout token revocation

Revision ID: c2d3e4f5a6b7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-17 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "c2d3e4f5a6b7"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f6"
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
