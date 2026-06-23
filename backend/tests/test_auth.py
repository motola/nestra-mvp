"""Auth unit tests — hashing, JWT, route registration. No database required."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND_ROOT / "src"))

from identity.security import (  # noqa: E402
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing(unittest.TestCase):
    def test_hash_then_verify(self) -> None:
        hashed = hash_password("hunter2")
        self.assertNotEqual(hashed, "hunter2")
        self.assertTrue(verify_password("hunter2", hashed))

    def test_wrong_password_fails(self) -> None:
        hashed = hash_password("hunter2")
        self.assertFalse(verify_password("not-it", hashed))


class TestAccessToken(unittest.TestCase):
    def test_roundtrip(self) -> None:
        token = create_access_token({"sub": "user-123", "org": "org-456"})
        payload = decode_access_token(token)
        self.assertIsNotNone(payload)
        assert payload is not None
        self.assertEqual(payload["sub"], "user-123")
        self.assertEqual(payload["org"], "org-456")

    def test_tampered_token_rejected(self) -> None:
        token = create_access_token({"sub": "x"})
        self.assertIsNone(decode_access_token(token + "tamper"))


class TestAuthRoutes(unittest.TestCase):
    def test_auth_routes_registered(self) -> None:
        from main import app

        paths = {route.path for route in app.routes}  # type: ignore[attr-defined]
        for path in ("/auth/signup", "/auth/login", "/auth/logout", "/me"):
            self.assertIn(path, paths)


if __name__ == "__main__":
    unittest.main()
