"""Tests for the device registry's deterministic identity."""

from __future__ import annotations

import unittest

from devices.registry import spire_device_id
from spire import SpireDevice


class DeviceIdentityTest(unittest.TestCase):
    def test_id_is_stable_for_the_same_identity(self) -> None:
        self.assertEqual(
            spire_device_id("shelly", "AA:BB:CC"), spire_device_id("shelly", "AA:BB:CC")
        )

    def test_distinct_identities_differ(self) -> None:
        self.assertNotEqual(spire_device_id("shelly", "1"), spire_device_id("shelly", "2"))

    def test_saved_id_matches_the_cloud_poll_id(self) -> None:
        # A device saved to the registry and the same device polled live must
        # resolve to ONE logical id — there is no second identity scheme.
        saved = str(spire_device_id("govee", "AA::H6159"))
        polled = SpireDevice.from_vendor(
            vendor="govee",
            vendor_id="AA::H6159",
            name="x",
            device_type="light",
            online=True,
        ).identity.id
        self.assertEqual(saved, polled)


if __name__ == "__main__":
    unittest.main()
