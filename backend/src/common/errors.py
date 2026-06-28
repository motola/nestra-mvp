"""Consistent API error model and global exception handlers.

Every failure — expected or not — returns the same JSON envelope, so clients get
a predictable shape instead of FastAPI's default (and unhandled errors never leak
a stack trace to the caller). Inspired by RFC 9457 (Problem Details), kept lean.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

# Map common statuses to a short machine-readable code.
_STATUS_CODES: dict[int, str] = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    409: "conflict",
    422: "validation_error",
    429: "rate_limited",
    500: "internal_error",
    502: "upstream_error",
    503: "unavailable",
    504: "upstream_timeout",
}


class ErrorResponse(BaseModel):
    """The single error envelope returned for every failure."""

    error: str  # short machine-readable code, e.g. "not_found"
    detail: str  # human-readable explanation
    status: int  # HTTP status code


def _code_for(status: int) -> str:
    return _STATUS_CODES.get(status, "error")


def _envelope(status: int, detail: str) -> JSONResponse:
    body = ErrorResponse(error=_code_for(status), detail=detail, status=status)
    return JSONResponse(status_code=status, content=body.model_dump())


async def _http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return _envelope(exc.status_code, str(exc.detail))


async def _validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    fields = ", ".join(".".join(str(p) for p in e["loc"]) for e in exc.errors())
    return _envelope(422, f"Invalid request data: {fields}")


async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Log the real error server-side; return a generic message so no stack trace
    # or internal detail leaks to the client.
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return _envelope(500, "An unexpected error occurred.")


def register_error_handlers(app: FastAPI) -> None:
    """Wire the consistent error envelope onto the app."""
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _unhandled_exception_handler)


def error_responses(*statuses: int) -> dict[int | str, dict[str, Any]]:
    """OpenAPI ``responses=`` helper so docs show the error shape for given statuses."""
    return {s: {"model": ErrorResponse, "description": _code_for(s)} for s in statuses}
