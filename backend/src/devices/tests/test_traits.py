"""Tests for capability-based device traits and deterministic device ids."""

from __future__ import annotations

import unittest

from devices.models import AlphaconDevice
from devices.traits import Trait, derive_traits


class DeriveTraitsTest(unittest.TestCase):
    def test_actuator_traits_come_from_commands(self) -> None:
        traits = derive_traits(["turn_on", "turn_off", "set_brightness", "set_color"])
        self.assertEqual(traits, [Trait.ON_OFF, Trait.DIMMABLE, Trait.COLOR])

    def test_reporting_traits_come_from_readings(self) -> None:
        traits = derive_traits([], reports_temperature=True, reports_leak=True)
        self.assertEqual(traits, [Trait.REPORTS_TEMPERATURE, Trait.REPORTS_LEAK])

    def test_no_capabilities_yields_no_traits(self) -> None:
        self.assertEqual(derive_traits([]), [])


class AlphaconDeviceTest(unittest.TestCase):
    def test_traits_are_auto_derived_from_canonical_fields(self) -> None:
        device = AlphaconDevice(
            vendor="govee",
            vendor_id="AA::H6159",
            name="Strip",
            type="light",
            online=True,
            controllable=True,
            supported_commands=["turn_on", "set_brightness"],
        )
        self.assertEqual(device.traits, [Trait.ON_OFF, Trait.DIMMABLE])

    def test_same_vendor_identity_yields_same_id(self) -> None:
        first = AlphaconDevice(
            vendor="govee",
            vendor_id="AA::H6159",
            name="x",
            type="light",
            online=True,
            controllable=True,
        )
        second = AlphaconDevice(
            vendor="govee",
            vendor_id="AA::H6159",
            name="x",
            type="light",
            online=True,
            controllable=True,
        )
        self.assertEqual(first.id, second.id)

    def test_explicit_id_is_preserved(self) -> None:
        device = AlphaconDevice(
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
