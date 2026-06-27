"""Tests for capability-based device capabilities derivation."""

from __future__ import annotations

import unittest

from spire.traits import Trait, derive_traits


class DeriveCapabilitiesTest(unittest.TestCase):
    def test_actuator_traits_come_from_commands(self) -> None:
        capabilities = derive_traits(["turn_on", "turn_off", "set_brightness", "set_color"])
        self.assertEqual(capabilities, [Trait.ON_OFF, Trait.DIMMABLE, Trait.COLOR])

    def test_reporting_traits_come_from_readings(self) -> None:
        capabilities = derive_traits([], reports_temperature=True, reports_leak=True)
        self.assertEqual(capabilities, [Trait.REPORTS_TEMPERATURE, Trait.REPORTS_LEAK])

    def test_no_capabilities_yields_no_traits(self) -> None:
        self.assertEqual(derive_traits([]), [])


if __name__ == "__main__":
    unittest.main()
