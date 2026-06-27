"""Migration sanity checks — no database required.

Verifies the Alembic baseline is well-formed and that the model metadata
matches the tables the baseline creates. Running migrations against a real
database is covered separately (see the dev/CI Postgres flow).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND_ROOT / "src"))

# Tables owned by the 0001 baseline migration.
_BASELINE_TABLES = {
    "organisations",
    "properties",
    "rooms",
    "devices",
    "alerts",
    "state_history",
}

# Tables added by the 0002 identity migration.
_IDENTITY_TABLES = {
    "users",
    "portfolios",
    "org_memberships",
    "sessions",
}


def _script_directory() -> ScriptDirectory:
    config = Config(str(_BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(_BACKEND_ROOT / "alembic"))
    return ScriptDirectory.from_config(config)


class TestBaselineMigration(unittest.TestCase):
    def test_single_head_is_0003(self) -> None:
        script = _script_directory()
        self.assertEqual(list(script.get_heads()), ["0003"])

    def test_baseline_is_the_root(self) -> None:
        script = _script_directory()
        base = script.get_revision("0001")
        self.assertIsNone(base.down_revision)

    def test_identity_revision_follows_baseline(self) -> None:
        script = _script_directory()
        self.assertEqual(script.get_revision("0002").down_revision, "0001")

    def test_rls_revision_follows_identity(self) -> None:
        script = _script_directory()
        self.assertEqual(script.get_revision("0003").down_revision, "0002")

    def test_metadata_matches_baseline_tables(self) -> None:
        from sqlmodel import SQLModel

        import core.tables  # noqa: F401  (registers tables on import)

        table_names = set(SQLModel.metadata.tables.keys())
        self.assertTrue(
            _BASELINE_TABLES.issubset(table_names),
            f"missing from metadata: {_BASELINE_TABLES - table_names}",
        )

    def test_metadata_includes_identity_tables(self) -> None:
        from sqlmodel import SQLModel

        import core.tables  # noqa: F401  (FK targets: organisations)
        import identity.models  # noqa: F401  (registers identity tables on import)

        table_names = set(SQLModel.metadata.tables.keys())
        self.assertTrue(
            _IDENTITY_TABLES.issubset(table_names),
            f"missing from metadata: {_IDENTITY_TABLES - table_names}",
        )


if __name__ == "__main__":
    unittest.main()
