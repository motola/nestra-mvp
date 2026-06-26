from __future__ import annotations

import logging
import logging.config
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from api.v1.router import router as v1_router
from config import get_settings
from identity.api import router as identity_router

# ── Logging ───────────────────────────────────────────────────────────────────

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["console"]},
        "loggers": {
            "uvicorn": {"propagate": True},
            "uvicorn.access": {"propagate": True},
        },
    }
)

logger = logging.getLogger(__name__)

_BACKEND_ROOT = Path(__file__).parent.parent


# ── Lifespan ──────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()

    mode = "DEMO" if settings.demo_mode else "LIVE"
    logger.info("Alphacon API starting — mode=%s", mode)

    # Run DB migrations
    try:
        from alembic.config import Config

        from alembic import command

        alembic_cfg = Config(str(_BACKEND_ROOT / "alembic.ini"))
        logger.info("Running Alembic migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations complete.")
    except Exception as exc:
        logger.warning("Alembic migration failed: %s", exc, exc_info=True)

    # Verify DB connectivity
    try:
        from db import engine

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connected")
    except Exception as exc:
        logger.warning("Database unreachable on startup: %s", exc)

    # Seed demo data
    if settings.demo_mode:
        from db import AsyncSessionLocal
        from demo.data import ensure_demo_seeded

        async with AsyncSessionLocal() as session:
            await ensure_demo_seeded(session)

    # Verify Upstash Redis connectivity
    if settings.upstash_redis_rest_url and settings.upstash_redis_rest_token:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                headers = {"Authorization": f"Bearer {settings.upstash_redis_rest_token}"}
                base = settings.upstash_redis_rest_url
                await client.get(f"{base}/set/startup_test/ok/ex/60", headers=headers)
                r = await client.get(f"{base}/get/startup_test", headers=headers)
                val = r.json().get("result") if r.status_code == 200 else None
            if val == "ok":
                logger.info("Redis connected — Upstash")
            else:
                logger.warning("Redis ping returned unexpected value: %r", val)
        except Exception as exc:
            logger.warning("Upstash Redis unreachable on startup: %s", exc)
    else:
        logger.warning(
            "UPSTASH_REDIS_REST_URL / UPSTASH_REDIS_REST_TOKEN not set — "
            "insight caching is disabled"
        )

    yield

    logger.info("Alphacon API shut down")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="AlphaCon API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)


from config import get_settings
from demo.routes import router as demo_router
from identity.api.routes import router as identity_router
from property.api.routes import router as property_router

_settings = get_settings()

app = FastAPI(
    title="AlphaCon API",
    version="0.1.0",
    docs_url="/docs" if _settings.debug else None,
    redoc_url="/redoc" if _settings.debug else None,
    openapi_url="/openapi.json" if _settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(demo_router)
app.include_router(identity_router)
app.include_router(property_router)
