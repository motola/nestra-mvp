from __future__ import annotations

import os
import sys

from sqlalchemy import create_engine, pool

from alembic import context

# Add src/ to path so model imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Imports below need src/ on the path (hence E402). Table models are imported so
# their metadata registers on SQLModel.metadata.
from sqlmodel import SQLModel  # noqa: E402

from config import get_settings as _get_settings  # noqa: E402
from core.tables import (  # noqa: E402, F401
    Alert,
    Device,
    Organisation,
    Property,
    Room,
    StateHistory,
)

config = context.config

# Skip fileConfig — the app configures its own logging in main.py.
# fileConfig would override the root logger level to WARN and suppress app logs.

target_metadata = SQLModel.metadata

# Pull DATABASE_URL from pydantic settings (reads .env); os.environ alone won't have it.
_raw_url = _get_settings().database_url or ""
_sync_url = _raw_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://").replace(
    "postgresql://", "postgresql+psycopg2://", 1
)
if _sync_url:
    config.set_main_option("sqlalchemy.url", _sync_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
