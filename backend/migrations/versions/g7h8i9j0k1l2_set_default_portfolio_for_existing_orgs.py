"""Set default portfolio for existing organizations.

Revision ID: g7h8i9j0k1l2
Revises: d6e7f8g9h0i1
Create Date: 2026-08-30

For organizations that don't have a default portfolio, sets their first
(oldest) portfolio as the default and ensures no other portfolios are marked
as default.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# Alembic metadata
revision = "g7h8i9j0k1l2"
down_revision = "d6e7f8g9h0i1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Set the oldest portfolio for each org as default if none exists."""
    connection = op.get_bind()

    # Check if any organizations lack a default portfolio
    check_stmt = sa.text("""
        SELECT COUNT(DISTINCT organization_id)
        FROM portfolios
        WHERE organization_id NOT IN (
            SELECT DISTINCT organization_id
            FROM portfolios
            WHERE is_default = TRUE
        )
    """)
    result = connection.execute(check_stmt)
    orgs_without_default = result.scalar() or 0

    # Skip migration if all organizations already have a default portfolio
    if orgs_without_default == 0:
        return

    # For each organization, if no portfolio has is_default=True,
    # set the oldest one as default
    update_stmt = sa.text("""
        UPDATE portfolios
        SET is_default = TRUE
        WHERE (organization_id, created_at) IN (
            SELECT organization_id, MIN(created_at)
            FROM portfolios
            WHERE organization_id NOT IN (
                SELECT DISTINCT organization_id
                FROM portfolios
                WHERE is_default = TRUE
            )
            GROUP BY organization_id
        )
    """)
    connection.execute(update_stmt)

    # Ensure only one default portfolio per organization
    # (set all others to false if somehow multiple exist)
    cleanup_stmt = sa.text("""
        UPDATE portfolios
        SET is_default = FALSE
        WHERE (organization_id, id) NOT IN (
            SELECT organization_id, id
            FROM portfolios p1
            WHERE is_default = TRUE
            AND (id = (
                SELECT id
                FROM portfolios p2
                WHERE p2.organization_id = p1.organization_id
                AND is_default = TRUE
                ORDER BY created_at ASC
                LIMIT 1
            ))
        )
        AND is_default = TRUE
    """)
    connection.execute(cleanup_stmt)


def downgrade() -> None:
    """Revert to no default portfolios."""
    connection = op.get_bind()
    reset_stmt = sa.text("UPDATE portfolios SET is_default = FALSE")
    connection.execute(reset_stmt)
