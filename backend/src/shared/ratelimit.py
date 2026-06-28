"""Per-client rate limiting (slowapi, in-memory per-process storage).

A generous default that protects the API from abuse without getting in a normal
UI's way. The 429 reuses the consistent error envelope from ``shared.errors``.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from shared.errors import ErrorResponse

# Per client IP. Generous for a UI, blocks hammering/abuse.
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])


async def _rate_limit_handler(_request: Request, _exc: RateLimitExceeded) -> JSONResponse:
    body = ErrorResponse(
        error="rate_limited", detail="Too many requests; please slow down.", status=429
    )
    return JSONResponse(status_code=429, content=body.model_dump())


def register_rate_limiting(app: FastAPI) -> None:
    """Attach the limiter, its 429 handler, and the enforcement middleware."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)  # type: ignore[arg-type]
    app.add_middleware(SlowAPIMiddleware)
