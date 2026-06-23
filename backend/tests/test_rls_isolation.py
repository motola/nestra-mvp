"""Proof that Row-Level Security isolates organisations.

Runs only when ``TEST_DATABASE_URL`` points at a Postgres where the connecting
role may ``CREATE ROLE`` (a local dev/CI database — never the shared Supabase
instance). It builds a probe table using the *same* policy expression as
migration 0003, then verifies that a non-BYPASSRLS role sees only the rows for
the organisation bound to ``app.current_organization_id`` — even with a
deliberately unfiltered ``SELECT *``.
"""

from __future__ import annotations

import os
import unittest
import uuid

try:
    import psycopg2
except ImportError:  # pragma: no cover
    psycopg2 = None  # type: ignore[assignment]

_TEST_DB = os.environ.get("TEST_DATABASE_URL")

# Mirror of the USING clause in alembic/versions/0003_rls_policies.py.
_USING = "organisation_id = nullif(current_setting('app.current_organization_id', true), '')::uuid"


@unittest.skipUnless(_TEST_DB and psycopg2, "set TEST_DATABASE_URL to a local Postgres")
class TestRlsIsolation(unittest.TestCase):
    def setUp(self) -> None:
        self.org_a = str(uuid.uuid4())
        self.org_b = str(uuid.uuid4())
        self.role = "rls_test_" + uuid.uuid4().hex[:8]
        self.conn = psycopg2.connect(_TEST_DB)
        self.conn.autocommit = True
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE rls_probe (id uuid PRIMARY KEY, organisation_id uuid NOT NULL)")
        cur.execute("ALTER TABLE rls_probe ENABLE ROW LEVEL SECURITY")
        cur.execute(f"CREATE POLICY rls_probe_org_isolation ON rls_probe USING ({_USING})")
        cur.execute("INSERT INTO rls_probe VALUES (%s, %s)", (str(uuid.uuid4()), self.org_a))
        cur.execute("INSERT INTO rls_probe VALUES (%s, %s)", (str(uuid.uuid4()), self.org_b))
        cur.execute(f"CREATE ROLE {self.role} NOLOGIN NOSUPERUSER NOBYPASSRLS")
        cur.execute(f"GRANT SELECT ON rls_probe TO {self.role}")

    def tearDown(self) -> None:
        cur = self.conn.cursor()
        cur.execute("DROP TABLE IF EXISTS rls_probe")
        cur.execute(f"DROP ROLE IF EXISTS {self.role}")
        self.conn.close()

    def _visible_orgs(self, org_context: str | None) -> set[str]:
        """Org ids visible via an unfiltered SELECT, as the restricted role."""
        self.conn.autocommit = False
        try:
            cur = self.conn.cursor()
            cur.execute(f"SET LOCAL ROLE {self.role}")
            if org_context is not None:
                cur.execute(
                    "SELECT set_config('app.current_organization_id', %s, true)", (org_context,)
                )
            cur.execute("SELECT organisation_id FROM rls_probe")
            return {str(row[0]) for row in cur.fetchall()}
        finally:
            self.conn.rollback()
            self.conn.autocommit = True

    def test_sees_only_scoped_org(self) -> None:
        self.assertEqual(self._visible_orgs(self.org_a), {self.org_a})
        self.assertEqual(self._visible_orgs(self.org_b), {self.org_b})

    def test_sees_nothing_without_context(self) -> None:
        self.assertEqual(self._visible_orgs(None), set())

    def test_bypassrls_admin_sees_all(self) -> None:
        cur = self.conn.cursor()
        cur.execute("SELECT count(*) FROM rls_probe")
        self.assertEqual(cur.fetchone()[0], 2)


if __name__ == "__main__":
    unittest.main()
