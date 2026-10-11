"""Fail when canonical persistence models cannot be served by the migrated schema."""

from __future__ import annotations

import ast
import asyncio
import sys
from collections import Counter
from pathlib import Path
from typing import Any, cast

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import ENUM as PostgreSQLEnum
from sqlalchemy.engine import Connection
from sqlalchemy.sql.schema import Table

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT / "src"))

import identity.repository.models  # noqa: E402,F401
import integrations.models  # noqa: E402,F401
import occupancy.repository.models  # noqa: E402,F401
import property.repository.models  # noqa: E402,F401
from db import engine  # noqa: E402
from integrations.models import IntegrationModel  # noqa: E402
from property.domain import (  # noqa: E402
    Capability,
    Device,
    DeviceCapability,
    DeviceCurrentState,
    DeviceIntegration,
    DevicePlacement,
    DeviceStateEvent,
    Integration,
)
from property.domain.audit import AuditEvent  # noqa: E402
from property.repository.models import (  # noqa: E402
    AuditEventModel,
    CapabilityModel,
    DeviceCapabilityModel,
    DeviceCurrentStateModel,
    DeviceIntegrationModel,
    DeviceModel,
    DevicePlacementModel,
    DeviceStateEventModel,
)

MIGRATION_DIR = BACKEND_ROOT / "migrations" / "versions"

MODEL_TABLES = (
    IntegrationModel,
    DeviceModel,
    DevicePlacementModel,
    DeviceIntegrationModel,
    CapabilityModel,
    DeviceCapabilityModel,
    DeviceCurrentStateModel,
    DeviceStateEventModel,
    AuditEventModel,
)

DOMAIN_MODEL_PAIRS = (
    (Integration, IntegrationModel),
    (Device, DeviceModel),
    (DevicePlacement, DevicePlacementModel),
    (DeviceIntegration, DeviceIntegrationModel),
    (Capability, CapabilityModel),
    (DeviceCapability, DeviceCapabilityModel),
    (DeviceCurrentState, DeviceCurrentStateModel),
    (DeviceStateEvent, DeviceStateEventModel),
    (AuditEvent, AuditEventModel),
)


def _literal_assignment(tree: ast.Module, name: str) -> Any:
    for node in tree.body:
        if isinstance(node, ast.Assign | ast.AnnAssign):
            target = node.target if isinstance(node, ast.AnnAssign) else node.targets[0]
            if isinstance(target, ast.Name) and target.id == name:
                if node.value is None:
                    raise ValueError(f"{name} has no value")
                return ast.literal_eval(node.value)
    raise ValueError(f"missing {name}")


def check_migration_graph() -> list[str]:
    """Check revision uniqueness, parent existence, roots, heads, and cycles."""
    errors: list[str] = []
    revisions: dict[str, tuple[str | None, Path]] = {}
    duplicates: Counter[str] = Counter()

    for path in sorted(MIGRATION_DIR.glob("*.py")):
        if path.name == "__init__.py":
            continue
        try:
            tree = ast.parse(path.read_text(), filename=str(path))
            revision = _literal_assignment(tree, "revision")
            down_revision = _literal_assignment(tree, "down_revision")
        except (SyntaxError, ValueError) as exc:
            errors.append(f"{path.name}: invalid Alembic metadata ({exc})")
            continue

        if not isinstance(revision, str):
            errors.append(f"{path.name}: revision must be a string")
            continue
        if down_revision is not None and not isinstance(down_revision, str):
            errors.append(f"{path.name}: merge/tuple down_revision is not supported")
            continue

        duplicates[revision] += 1
        revisions[revision] = (down_revision, path)

    for revision, count in duplicates.items():
        if count > 1:
            errors.append(f"duplicate migration revision {revision!r} appears {count} times")

    referenced = {parent for parent, _ in revisions.values() if parent is not None}
    for revision, (parent, path) in revisions.items():
        if parent is not None and parent not in revisions:
            errors.append(f"{path.name}: missing parent revision {parent!r}")

        seen: set[str] = set()
        cursor: str | None = revision
        while cursor is not None and cursor in revisions:
            if cursor in seen:
                errors.append(f"cycle detected from revision {revision!r}")
                break
            seen.add(cursor)
            cursor = revisions[cursor][0]

    roots = [revision for revision, (parent, _) in revisions.items() if parent is None]
    heads = [revision for revision in revisions if revision not in referenced]
    if len(roots) != 1:
        errors.append(f"expected one migration root, found {roots}")
    if len(heads) != 1:
        errors.append(f"expected one migration head, found {heads}")

    return errors


def check_domain_models() -> list[str]:
    """Ensure domain fields are persistable by their canonical ORM model."""
    errors: list[str] = []
    for domain_model, orm_model in DOMAIN_MODEL_PAIRS:
        domain_fields = set(domain_model.model_fields)
        orm_fields = set(orm_model.__table__.columns.keys())
        missing = sorted(domain_fields - orm_fields)
        if missing:
            errors.append(
                f"{domain_model.__name__} fields missing from {orm_model.__name__}: {missing}"
            )
        required_only_in_orm = sorted(
            column.name
            for column in orm_model.__table__.columns
            if column.name not in domain_fields
            and column.nullable is False
            and column.default is None
            and column.server_default is None
        )
        if required_only_in_orm:
            errors.append(
                f"{orm_model.__name__} requires fields absent from "
                f"{domain_model.__name__}: {required_only_in_orm}"
            )
    return errors


def _check_database(connection: Connection) -> list[str]:
    inspector = inspect(connection)
    database_tables = set(inspector.get_table_names())
    errors: list[str] = []

    for model in MODEL_TABLES:
        table = cast(Table, model.__table__)
        if table.name not in database_tables:
            errors.append(f"database is missing ORM table {table.name!r}")
            continue

        database_columns = {column["name"]: column for column in inspector.get_columns(table.name)}
        orm_columns = {column.name: column for column in table.columns}

        for name, orm_column in orm_columns.items():
            database_column = database_columns.get(name)
            if database_column is None:
                errors.append(f"{table.name}.{name}: ORM column is missing from database")
                continue
            if orm_column.nullable is False and database_column["nullable"] is True:
                errors.append(
                    f"{table.name}.{name}: ORM requires NOT NULL but database allows NULL"
                )
            database_type = database_column["type"]
            type_matches = orm_column.type._compare_type_affinity(database_type)
            if isinstance(orm_column.type, sa.Enum):
                type_matches = (
                    isinstance(database_type, PostgreSQLEnum)
                    and orm_column.type.name == database_type.name
                    and set(orm_column.type.enums) == set(database_type.enums)
                )
            if not type_matches and str(orm_column.type) != str(database_type):
                errors.append(
                    f"{table.name}.{name}: ORM type {orm_column.type} does not match "
                    f"database type {database_column['type']}"
                )

        # Compatibility columns may remain during a forward-only migration,
        # but they must not make an ORM insert impossible.
        for name, database_column in database_columns.items():
            if name in orm_columns:
                continue
            if (
                database_column["nullable"] is False
                and database_column.get("default") is None
                and name not in {"id"}
            ):
                errors.append(
                    f"{table.name}.{name}: required legacy column has no server default; "
                    "canonical ORM inserts will fail"
                )

    return errors


async def check_database() -> list[str]:
    async with engine.connect() as connection:
        return await connection.run_sync(_check_database)


async def main() -> int:
    errors = [*check_migration_graph(), *check_domain_models(), *await check_database()]
    await engine.dispose()
    if errors:
        print("Database consistency check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    tables = ", ".join(cast(Table, model.__table__).name for model in MODEL_TABLES)
    print(f"Database consistency check passed for: {tables}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
