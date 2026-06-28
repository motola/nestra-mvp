"""Tests for API hardening: pagination and the error envelope."""

from __future__ import annotations

import unittest

from common.errors import ErrorResponse
from common.pagination import PageParams, paginate


class PaginateTest(unittest.TestCase):
    def test_no_limit_returns_everything(self) -> None:
        self.assertEqual(paginate([1, 2, 3], PageParams()), [1, 2, 3])

    def test_limit_and_offset(self) -> None:
        self.assertEqual(paginate([1, 2, 3, 4, 5], PageParams(limit=2, offset=1)), [2, 3])

    def test_offset_only(self) -> None:
        self.assertEqual(paginate([1, 2, 3], PageParams(offset=2)), [3])

    def test_offset_past_end_is_empty(self) -> None:
        self.assertEqual(paginate([1, 2], PageParams(offset=5)), [])


class ErrorEnvelopeTest(unittest.TestCase):
    def test_shape(self) -> None:
        body = ErrorResponse(error="not_found", detail="Device not found", status=404)
        self.assertEqual(
            body.model_dump(),
            {"error": "not_found", "detail": "Device not found", "status": 404},
        )


if __name__ == "__main__":
    unittest.main()
