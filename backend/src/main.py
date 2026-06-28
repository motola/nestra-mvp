from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from demo.routes import router as demo_router
from identity.api.routes import router as identity_router
from intelligence.api.routes import router as intelligence_router
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
app.include_router(intelligence_router)
app.include_router(property_router)
