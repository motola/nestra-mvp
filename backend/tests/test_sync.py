"""Tests for the device factory and the sync orchestration."""

from __future__ import annotations

import asyncio
import unittest

from integrations.factory import create_device_data
from integrations.sync import DeviceSyncService
from spire.device import DeviceIdentity, SpireDevice, SpireIdentifier, VendorRef
from spire.traits import Trait


def _device(value: str = "AA::H6159") -> SpireDevice:
    return SpireDevice(
        identity=DeviceIdentity(identifier=SpireIdentifier(system="govee", value=value)),
        vendor=VendorRef(vendor="govee", vendor_name="Govee Strip"),
        traits=[Trait.ON_OFF],
    )


class FactoryTest(unittest.TestCase):
    def test_stamps_context_without_touching_identity_or_name(self) -> None:
        device = _device()
        original_id = device.identity.id
        stamped = create_device_data(
            device, organization_id="org1", property_id="prop1", integration_id="int1"
        )
        self.assertEqual(stamped.placement.organization_id, "org1")
        self.assertEqual(stamped.placement.property_id, "prop1")
        self.assertEqual(stamped.meta.source, "int1")
        self.assertIsNotNone(stamped.meta.last_synced_at)
        self.assertEqual(stamped.identity.id, original_id)
        self.assertIsNone(stamped.naming.display_name)


class SyncServiceTest(unittest.TestCase):
    def test_fetches_stamps_and_upserts_each_device(self) -> None:
        fetched = [_device("d1"), _device("d2")]
        upserted: list[SpireDevice] = []

        async def fake_fetch() -> list[SpireDevice]:
            return fetched

        async def fake_upsert(device: SpireDevice) -> None:
            upserted.append(device)

        service = DeviceSyncService(fetch=fake_fetch, upsert=fake_upsert)
        count = asyncio.run(service.sync_integration(organization_id="org1", integration_id="int1"))

        self.assertEqual(count, 2)
        self.assertEqual(len(upserted), 2)
        self.assertTrue(all(d.placement.organization_id == "org1" for d in upserted))
        self.assertTrue(all(d.meta.source == "int1" for d in upserted))


if __name__ == "__main__":
    unittest.main()
