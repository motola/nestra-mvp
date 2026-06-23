"""Row-Level Security policies on org-scoped tables.

Enables RLS and an org-isolation policy on every table that carries
``organisation_id``. The policy compares the row's org against the
``app.current_organization_id`` setting (see ``shared.tenant``). With
``missing_ok = true`` an unset context yields NULL, so a non-BYPASSRLS role
sees no rows until a scope is set.

Note: the application currently connects as a BYPASSRLS role, so these policies
are inert for the app today (demo unaffected) but enforce isolation for any
restricted role — proven in ``tests/test_rls_isolation.py``.

Revision ID: 0003
Revises: 0002
"""

from __future__ import annotations

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

_RLS_TABLES = ("properties", "portfolios", "org_memberships")
_USING = "organisation_id = nullif(current_setting('app.current_organization_id', true), '')::uuid"


def upgrade() -> None:
    for table in _RLS_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"CREATE POLICY {table}_org_isolation ON {table} USING ({_USING})")


def downgrade() -> None:
    for table in _RLS_TABLES:
        op.execute(f"DROP POLICY IF EXISTS {table}_org_isolation ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
