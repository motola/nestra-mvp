from __future__ import annotations

import unittest


class TestSmoke(unittest.TestCase):
    def test_shared_package_importable(self) -> None:
        import shared  # noqa: F401
