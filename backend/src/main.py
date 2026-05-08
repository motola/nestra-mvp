from __future__ import annotations

import logging
import logging.config
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.router import router as v1_router
from config import get_settings

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


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()

    # Log startup mode
    mode = "DEMO" if settings.demo_mode else "LIVE"
    logger.info("Alphacon API starting — mode=%s", mode)

    if settings.demo_mode:
        from demo.data import DEMO_PROPERTIES, DEMO_DEVICES
        logger.info(
            "Demo data loaded — %d properties, %d devices",
            len(DEMO_PROPERTIES),
            len(DEMO_DEVICES),
        )

    # Verify Supabase connectivity
    if settings.supabase_url and settings.supabase_service_role_key:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(
                    f"{settings.supabase_url}/rest/v1/",
                    headers={
                        "apikey": settings.supabase_service_role_key,
                        "Authorization": f"Bearer {settings.supabase_service_role_key}",
                    },
                )
            if r.status_code < 500:
                logger.info("Supabase connected — %s", settings.supabase_url)
            else:
                logger.warning(
                    "Supabase returned %s on startup ping — check credentials",
                    r.status_code,
                )
        except Exception as exc:
            logger.warning("Supabase unreachable on startup: %s", exc)
    else:
        logger.warning(
            "SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set — "
            "registry and alert features will be disabled"
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


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
