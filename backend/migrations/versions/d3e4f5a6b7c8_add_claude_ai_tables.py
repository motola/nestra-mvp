"""Add Claude AI integration tables.

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-08-25 12:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = "d3e4f5a6b7c8"
down_revision = "b3c4d5e6f7a8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # user_consents table
    op.create_table(
        "user_consents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("portfolio_access", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("device_access", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("historical_data_access", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("consented_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_user_consents_user_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_user_consents_user_id"),
    )

    # ai_conversations table
    op.create_table(
        "ai_conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_message", sa.String(5000), nullable=False),
        sa.Column("ai_response", sa.String(5000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_ai_conversations_user_id"),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_ai_conversations_organization_id",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ai_generated_reports table
    op.create_table(
        "ai_generated_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.String(10000), nullable=False),
        sa.Column("report_type", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_ai_generated_reports_user_id"),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_ai_generated_reports_organization_id",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ai_action_logs table
    op.create_table(
        "ai_action_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_type", sa.String(100), nullable=False),
        sa.Column("action_status", sa.String(50), nullable=False),
        sa.Column("details", sa.String(1000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_ai_action_logs_user_id"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("ai_action_logs")
    op.drop_table("ai_generated_reports")
    op.drop_table("ai_conversations")
    op.drop_table("user_consents")
