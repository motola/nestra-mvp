"""Tests for trait derivation and the formal trait catalog."""

from __future__ import annotations

import unittest

from spire.traits import TRAIT_CATALOG, Command, Trait, commands_for, derive_traits


class DeriveTraitsTest(unittest.TestCase):
    def test_actuator_traits_come_from_commands(self) -> None:
        traits = derive_traits(["turn_on", "turn_off", "set_brightness", "set_color"])
        self.assertEqual(traits, [Trait.ON_OFF, Trait.DIMMABLE, Trait.COLOR])

    def test_reporting_traits_come_from_readings(self) -> None:
        traits = derive_traits([], reports_temperature=True, reports_leak=True)
        self.assertEqual(traits, [Trait.REPORTS_TEMPERATURE, Trait.REPORTS_LEAK])

    def test_no_capabilities_yields_no_traits(self) -> None:
        self.assertEqual(derive_traits([]), [])


class TraitCatalogTest(unittest.TestCase):
    def test_every_trait_has_a_spec(self) -> None:
        # Completeness: no trait may exist without a formal contract.
        missing = [t for t in Trait if t not in TRAIT_CATALOG]
        self.assertEqual(missing, [], f"traits missing a spec: {missing}")

    def test_actuators_have_commands_sensors_do_not(self) -> None:
        for trait, spec in TRAIT_CATALOG.items():
            if spec.kind == "actuator":
                self.assertTrue(spec.commands, f"{trait} is an actuator but has no commands")
            else:
                self.assertEqual(spec.commands, (), f"{trait} is a sensor but lists commands")

    def test_commands_for_collects_actuator_commands(self) -> None:
        cmds = commands_for([Trait.ON_OFF, Trait.DIMMABLE])
        self.assertEqual(cmds, ["turn_on", "turn_off", "set_brightness"])

    def test_command_model(self) -> None:
        self.assertEqual(Command(action="set_brightness", value=80).value, 80)


if __name__ == "__main__":
    unittest.main()
