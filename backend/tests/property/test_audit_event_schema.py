"""Regression checks for the audit event ORM/database contract."""

from __future__ import annotations

from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import asyncpg

from property.repository.models import AuditEventModel


def test_audit_insert_does_not_require_native_postgres_enums() -> None:
    """Audit columns are varchar in migrations, so INSERT binds must be varchar too."""
    statement = insert(AuditEventModel).values(
        actor_type="user",
        action="device_created",
        resource_type="device",
        status="success",
    )

    sql = str(statement.compile(dialect=asyncpg.dialect()))

    assert "auditactortype" not in sql
    assert "auditaction" not in sql
    assert "auditresourcetype" not in sql
    assert "auditstatus" not in sql
    assert "::VARCHAR" in sql
    assert "::JSONB" in sql
