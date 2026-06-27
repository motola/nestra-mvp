"""Tests for the unified SPIRE device resource model."""

from __future__ import annotations

import unittest

from spire.device import (
    AuditMeta,
    Connectivity,
    DeviceCategory,
    DeviceIdentity,
    DeviceNaming,
    DevicePlacement,
    DeviceStatus,
    SpireDevice,
    SpireIdentifier,
    VendorRef,
)
from spire.traits import Trait


def _device(**overrides: object) -> SpireDevice:
    base: dict[str, object] = {
        "identity": DeviceIdentity(identifier=SpireIdentifier(system="govee", value="AA::H6159")),
        "vendor": VendorRef(vendor="govee", vendor_name="Govee RGB Strip"),
    }
    base.update(overrides)
    return SpireDevice(**base)  # type: ignore[arg-type]


class IdentityTest(unittest.TestCase):
    def test_id_is_derived_from_identifier(self) -> None:
        first = DeviceIdentity(identifier=SpireIdentifier(system="govee", value="AA::H6159"))
        second = DeviceIdentity(identifier=SpireIdentifier(system="govee", value="AA::H6159"))
        self.assertEqual(first.id, second.id)

    def test_explicit_id_is_preserved(self) -> None:
        identity = DeviceIdentity(
            id="fixed-1", identifier=SpireIdentifier(system="govee", value="AA::H6159")
        )
        self.assertEqual(identity.id, "fixed-1")


class LabelTest(unittest.TestCase):
    def test_user_name_wins(self) -> None:
        device = _device(naming=DeviceNaming(display_name="Front desk lamp"))
        self.assertEqual(device.label, "Front desk lamp")

    def test_falls_back_to_vendor_name(self) -> None:
        self.assertEqual(_device().label, "Govee RGB Strip")

    def test_falls_back_to_identifier(self) -> None:
        device = _device(vendor=VendorRef(vendor="govee"))
        self.assertEqual(device.label, "Device AA::H6159")


class CapabilityTest(unittest.TestCase):
    def test_supports(self) -> None:
        device = _device(traits=[Trait.ON_OFF, Trait.DIMMABLE])
        self.assertTrue(device.supports(Trait.ON_OFF))
        self.assertFalse(device.supports(Trait.COLOR))


class OwnershipGroupsTest(unittest.TestCase):
    def test_groups_are_distinct_objects(self) -> None:
        device = _device()
        self.assertIsInstance(device.identity, DeviceIdentity)
        self.assertIsInstance(device.vendor, VendorRef)
        self.assertIsInstance(device.naming, DeviceNaming)
        self.assertIsInstance(device.placement, DevicePlacement)
        self.assertIsInstance(device.connectivity, Connectivity)
        self.assertIsInstance(device.meta, AuditMeta)


class LifecycleAndPlacementTest(unittest.TestCase):
    def test_defaults_to_active_and_uncategorised(self) -> None:
        device = _device()
        self.assertEqual(device.status, DeviceStatus.ACTIVE)
        self.assertEqual(device.category, DeviceCategory.OTHER)

    def test_placement_holds_property_and_room(self) -> None:
        device = _device(placement=DevicePlacement(property_id="p1", room_id="r1"))
        self.assertEqual(device.placement.property_id, "p1")
        self.assertEqual(device.placement.room_id, "r1")

    def test_online_accessor_reads_connectivity(self) -> None:
        device = _device(connectivity=Connectivity(online=True, ip_address="10.0.0.5"))
        self.assertTrue(device.online)
        self.assertEqual(device.connectivity.ip_address, "10.0.0.5")


class ApiSerialisationTest(unittest.TestCase):
    def test_controllable_derives_from_actuator_traits(self) -> None:
        self.assertTrue(_device(traits=[Trait.ON_OFF]).controllable)
        self.assertFalse(_device(traits=[Trait.REPORTS_POWER]).controllable)

    def test_to_api_produces_flat_frontend_shape(self) -> None:
        device = _device(
            category=DeviceCategory.LIGHT,
            connectivity=Connectivity(online=True),
            placement=DevicePlacement(property_id="p1", room_id="r1"),
            traits=[Trait.ON_OFF, Trait.DIMMABLE],
            supported_commands=["turn_on", "set_brightness"],
            state={"on": True, "power": 12.3},
        )
        api = device.to_api()
        self.assertEqual(api["vendor_id"], "AA::H6159")
        self.assertEqual(api["type"], "light")
        self.assertTrue(api["online"])
        self.assertTrue(api["controllable"])
        self.assertEqual(api["power_draw"], 12.3)
        self.assertEqual(api["property_id"], "p1")
        self.assertEqual(api["traits"], ["on_off", "dimmable"])


if __name__ == "__main__":
    unittest.main()
