"""Tests for the unified SPIRE device resource model."""

from __future__ import annotations

import unittest

from devices.capabilities import Capability
from devices.spire import (
    AuditMeta,
    DeviceIdentity,
    DeviceNaming,
    SpireDevice,
    SpireIdentifier,
    VendorRef,
)


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
        device = _device(capabilities=[Capability.ON_OFF, Capability.DIMMABLE])
        self.assertTrue(device.supports(Capability.ON_OFF))
        self.assertFalse(device.supports(Capability.COLOR))


class OwnershipGroupsTest(unittest.TestCase):
    def test_groups_are_distinct_objects(self) -> None:
        device = _device()
        self.assertIsInstance(device.identity, DeviceIdentity)
        self.assertIsInstance(device.vendor, VendorRef)
        self.assertIsInstance(device.naming, DeviceNaming)
        self.assertIsInstance(device.meta, AuditMeta)


if __name__ == "__main__":
    unittest.main()
