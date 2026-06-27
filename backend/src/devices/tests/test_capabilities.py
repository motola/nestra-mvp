"""Tests for capability-based device capabilities and deterministic device ids."""

from __future__ import annotations

import unittest

from devices.capabilities import Capability, derive_capabilities
from devices.models import SpireDevice


class DeriveCapabilitiesTest(unittest.TestCase):
    def test_actuator_traits_come_from_commands(self) -> None:
        capabilities = derive_capabilities(["turn_on", "turn_off", "set_brightness", "set_color"])
        self.assertEqual(capabilities, [Capability.ON_OFF, Capability.DIMMABLE, Capability.COLOR])

    def test_reporting_traits_come_from_readings(self) -> None:
        capabilities = derive_capabilities([], reports_temperature=True, reports_leak=True)
        self.assertEqual(capabilities, [Capability.REPORTS_TEMPERATURE, Capability.REPORTS_LEAK])

    def test_no_capabilities_yields_no_traits(self) -> None:
        self.assertEqual(derive_capabilities([]), [])


class SpireDeviceTest(unittest.TestCase):
    def test_traits_are_auto_derived_from_canonical_fields(self) -> None:
        device = SpireDevice(
            vendor="govee",
            vendor_id="AA::H6159",
            name="Strip",
            type="light",
            online=True,
            controllable=True,
            supported_commands=["turn_on", "set_brightness"],
        )
        self.assertEqual(device.capabilities, [Capability.ON_OFF, Capability.DIMMABLE])

    def test_same_vendor_identity_yields_same_id(self) -> None:
        first = SpireDevice(
            vendor="govee",
            vendor_id="AA::H6159",
            name="x",
            type="light",
            online=True,
            controllable=True,
        )
        second = SpireDevice(
            vendor="govee",
            vendor_id="AA::H6159",
            name="x",
            type="light",
            online=True,
            controllable=True,
        )
        self.assertEqual(first.id, second.id)

    def test_explicit_id_is_preserved(self) -> None:
        device = SpireDevice(
            id="fixed-1",
            vendor="govee",
            vendor_id="AA::H6159",
            name="x",
            type="light",
            online=True,
            controllable=True,
        )
        self.assertEqual(device.id, "fixed-1")


if __name__ == "__main__":
    unittest.main()
