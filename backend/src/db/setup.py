"""
Database setup — verifies schema and seeds a default organisation on startup.

Called from main.py lifespan. Uses httpx + PostgREST, consistent with the
rest of the codebase. No supabase-py client required.

Usage in main.py lifespan:
    from db.setup import setup_database
    db_ok = await setup_database(settings)
    if not db_ok:
        logger.warning(
            "Starting with incomplete database — some features may not work"
        )
"""

from __future__ import annotations

import logging

import httpx

from config import Settings

logger = logging.getLogger(__name__)

REQUIRED_TABLES = [
    "organisations",
    "properties",
    "rooms",
    "devices",
    "alerts",
    "state_history",
]


def _headers(settings: Settings) -> dict[str, str]:
    return {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
    }


async def verify_schema(settings: Settings) -> bool:
    """
    Check all required tables exist via PostgREST.
    Returns True if every table responds with 200.
    """
    all_good = True

    async with httpx.AsyncClient(timeout=10.0) as client:
        for table in REQUIRED_TABLES:
            try:
                r = await client.get(
                    f"{settings.supabase_url}/rest/v1/{table}",
                    headers=_headers(settings),
                    params={"select": "id", "limit": "1"},
                )
                if r.status_code == 200:
                    logger.info("✓ %s", table)
                else:
                    logger.error(
                        "✗ %s missing or inaccessible (HTTP %s) — "
                        "run migrations: alembic upgrade head",
                        table,
                        r.status_code,
                    )
                    all_good = False
            except Exception as exc:
                logger.error("✗ %s check failed: %s", table, exc)
                all_good = False

    return all_good


async def seed_organisation(settings: Settings) -> str | None:
    """
    Ensure a default organisation exists.
    Returns the org UUID, or None on failure.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{settings.supabase_url}/rest/v1/organisations",
                headers=_headers(settings),
                params={"select": "id", "limit": "1"},
            )

            if r.status_code == 200 and r.json():
                org_id = str(r.json()[0]["id"])
                logger.info("✓ Organisation: %s", org_id)
                return org_id

            # No org exists — create the default
            r = await client.post(
                f"{settings.supabase_url}/rest/v1/organisations",
                headers={**_headers(settings), "Prefer": "return=representation"},
                json={"name": "Alphacon Demo", "plan": "free"},
            )
            r.raise_for_status()
            rows = r.json()
            org_id = str((rows[0] if isinstance(rows, list) else rows)["id"])
            logger.info("✓ Created default organisation: %s", org_id)
            return org_id

    except Exception as exc:
        logger.error("✗ Organisation setup failed: %s", exc)
        return None


async def setup_database(settings: Settings) -> bool:
    """
    Main entry point called from main.py lifespan.

    Verifies schema, seeds a default organisation, and returns True
    if the database is ready for normal operation.
    """
    if not settings.supabase_url or not settings.supabase_service_role_key:
        logger.warning("Supabase not configured — skipping schema verification")
        return False

    logger.info("Verifying database schema...")

    schema_ok = await verify_schema(settings)

    if not schema_ok:
        logger.error(
            "\n"
            "    ════════════════════════════════\n"
            "    DATABASE NOT READY\n"
            "\n"
            "    Run the database migrations:\n"
            "    alembic upgrade head (runs automatically on startup)\n"
            "\n"
            "    Then restart the backend.\n"
            "    ════════════════════════════════"
        )
        return False

    org_id = await seed_organisation(settings)

    if not org_id:
        logger.error("✗ Failed to get or create organisation")
        return False

    logger.info("✓ Database ready")
    return True
