"""Password hashing and JWT helpers for the Identity context."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, Final

import bcrypt
from jose import JWTError, jwt

from config import get_settings

# bcrypt is used directly rather than via passlib: passlib 1.7.4 is incompatible
# with bcrypt 5.x on Python 3.14 (it errors on an internal version probe).
_BCRYPT_MAX_BYTES: Final[int] = 72  # bcrypt ignores input beyond 72 bytes
_ALGORITHM: Final[str] = "HS256"
ACCESS_TOKEN_TTL: Final[timedelta] = timedelta(days=7)


def hash_password(password: str) -> str:
    digest = bcrypt.hashpw(password.encode("utf-8")[:_BCRYPT_MAX_BYTES], bcrypt.gensalt())
    return digest.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8")[:_BCRYPT_MAX_BYTES], password_hash.encode("utf-8")
        )
    except ValueError:
        return False


def create_access_token(claims: dict[str, Any], ttl: timedelta = ACCESS_TOKEN_TTL) -> str:
    payload = {**claims, "exp": datetime.now(UTC) + ttl}
    return jwt.encode(payload, get_settings().secret_key, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, get_settings().secret_key, algorithms=[_ALGORITHM])
    except JWTError:
        return None
