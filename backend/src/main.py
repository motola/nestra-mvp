from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from identity.api.routes import router as identity_router
from integrations.api.oauth import router as oauth_router
from integrations.govee.routes import router as govee_router
from integrations.wifi.routes import router as wifi_router
from intelligence.api.routes import router as intelligence_router
from property.api.device_routes import router as device_router
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
    allow_origins=[
        "http://localhost:3000",
        "https://nestra-mvp.fly.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors with user-friendly messages instead of tracebacks."""
    errors = exc.errors()
    messages: list[str] = []
    for error in errors:
        field = ".".join(str(x) for x in error["loc"][1:])
        msg = error.get("msg", "Invalid value")
        messages.append(f"{field}: {msg}" if field else msg)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": " | ".join(messages)},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(identity_router)
app.include_router(intelligence_router)
app.include_router(oauth_router)
app.include_router(property_router)
app.include_router(device_router)
app.include_router(wifi_router)
app.include_router(govee_router)
