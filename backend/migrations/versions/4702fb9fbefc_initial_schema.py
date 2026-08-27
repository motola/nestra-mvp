"""Initial schema

Revision ID: 4702fb9fbefc
Revises:
Create Date: 2026-08-14 20:20:07.114796

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from alembic import op

revision: str = "4702fb9fbefc"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create organizations table
    op.create_table(
        "organizations",
        sa.Column("id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("legal_name", sa.String(255), nullable=False),
        sa.Column(
            "status", sa.Enum("ACTIVE", "SUSPENDED", "CANCELLED", name="org_status"), nullable=False
        ),
        sa.Column(
            "subscription_tier",
            sa.Enum("STARTER", "PROFESSIONAL", "ENTERPRISE", name="subscription_tier"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_org_slug"),
    )

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "auth_method",
            sa.Enum("PASSWORD", "MAGIC_LINK", "GOOGLE_SSO", "APPLE_SSO", name="auth_method"),
            nullable=False,
        ),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_tenant_only", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_user_email"),
    )

    # Create portfolios table
    op.create_table(
        "portfolios",
        sa.Column("id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1000), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "name", name="uq_portfolio_org_name"),
    )

    # Create org_memberships table
    op.create_table(
        "org_memberships",
        sa.Column("id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "org_role", sa.Enum("OWNER", "ORG_ADMIN", "BILLING", name="org_role"), nullable=False
        ),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("invited_by", pg.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["invited_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "organization_id", name="uq_org_membership"),
    )

    # Create sessions table
    op.create_table(
        "sessions",
        sa.Column("id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column("active_organization_id", pg.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "auth_method",
            sa.Enum("PASSWORD", "MAGIC_LINK", "GOOGLE_SSO", "APPLE_SSO", name="auth_method"),
            nullable=False,
        ),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["active_organization_id"],
            ["organizations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("sessions")
    op.drop_table("org_memberships")
    op.drop_table("portfolios")
    op.drop_table("users")
    op.drop_table("organizations")

    # Drop enums
    sa.Enum(name="org_role").drop(op.get_bind())
    sa.Enum(name="auth_method").drop(op.get_bind())
    sa.Enum(name="subscription_tier").drop(op.get_bind())
    sa.Enum(name="org_status").drop(op.get_bind())
