"""Intelligence Service — AI-driven device control via Claude API."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import get_settings
from api.routes import router as intelligence_router

_settings = get_settings()

app = FastAPI(
    title="Intelligence Service",
    version="0.1.0",
    docs_url="/docs" if _settings.debug else None,
    redoc_url="/redoc" if _settings.debug else None,
    openapi_url="/openapi.json" if _settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "intelligence"}


app.include_router(intelligence_router)
