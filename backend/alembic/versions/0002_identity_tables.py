"""Identity & Access tables — users, portfolios, org memberships, sessions.

Adds the auth foundation. The ``organisations`` table (from 0001) is reused for
the Organization aggregate, so it is not recreated here.

Revision ID: 0002
Revises: 0001
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("auth_method", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_tenant_only", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "portfolios",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organisation_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["organisation_id"], ["organisations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_portfolios_organisation_id", "portfolios", ["organisation_id"])

    op.create_table(
        "org_memberships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("organisation_id", sa.Uuid(), nullable=False),
        sa.Column("org_role", sa.String(), nullable=False),
        sa.Column("joined_at", sa.DateTime(), nullable=True),
        sa.Column("invited_by", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["organisation_id"], ["organisations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "organisation_id", name="uq_org_membership"),
    )
    op.create_index("ix_org_memberships_user_id", "org_memberships", ["user_id"])
    op.create_index("ix_org_memberships_organisation_id", "org_memberships", ["organisation_id"])

    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("active_organisation_id", sa.Uuid(), nullable=False),
        sa.Column("auth_method", sa.String(), nullable=False),
        sa.Column("issued_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["active_organisation_id"], ["organisations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])


def downgrade() -> None:
    op.drop_table("sessions")
    op.drop_table("org_memberships")
    op.drop_table("portfolios")
    op.drop_table("users")
