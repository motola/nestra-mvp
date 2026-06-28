"""Tests for the SPIRE property, room, occupant, and event resources."""

from __future__ import annotations

import unittest

from spire import (
    EventType,
    SpireEvent,
    SpireOccupant,
    SpireProperty,
    SpireRoom,
)
from spire.traits import Trait


class PublicApiTest(unittest.TestCase):
    def test_new_resources_are_exported_from_spire(self) -> None:
        from spire import (  # noqa: PLC0415 — asserting the public import path works
            EventType,
            SpireEvent,
            SpireOccupant,
            SpireProperty,
            SpireRoom,
        )

        self.assertIsNotNone(SpireProperty)
        self.assertIsNotNone(SpireRoom)
        self.assertIsNotNone(SpireOccupant)
        self.assertIsNotNone(SpireEvent)
        self.assertIsNotNone(EventType)


class PropertyTest(unittest.TestCase):
    def test_resource_type_is_property(self) -> None:
        prop = SpireProperty(id="prop-1", name="Maple Court")
        self.assertEqual(prop.resource_type, "Property")

    def test_optional_fields_default_to_none(self) -> None:
        prop = SpireProperty(id="prop-1", name="Maple Court")
        self.assertIsNone(prop.organization_id)
        self.assertIsNone(prop.address)
        self.assertIsNone(prop.timezone)

    def test_holds_organization_and_location(self) -> None:
        prop = SpireProperty(
            id="prop-1",
            organization_id="org-1",
            name="Maple Court",
            address="1 Maple St",
            timezone="Europe/London",
        )
        self.assertEqual(prop.organization_id, "org-1")
        self.assertEqual(prop.address, "1 Maple St")
        self.assertEqual(prop.timezone, "Europe/London")


class RoomTest(unittest.TestCase):
    def test_resource_type_is_room(self) -> None:
        room = SpireRoom(id="room-1", property_id="prop-1", name="Kitchen")
        self.assertEqual(room.resource_type, "Room")

    def test_belongs_to_property_and_records_floor(self) -> None:
        room = SpireRoom(id="room-1", property_id="prop-1", name="Kitchen", floor=2)
        self.assertEqual(room.property_id, "prop-1")
        self.assertEqual(room.floor, 2)


class OccupantTest(unittest.TestCase):
    def test_resource_type_is_occupant(self) -> None:
        occupant = SpireOccupant(id="occ-1", property_id="prop-1", name="Alex Tenant")
        self.assertEqual(occupant.resource_type, "Occupant")

    def test_holds_contact_details_and_room(self) -> None:
        occupant = SpireOccupant(
            id="occ-1",
            property_id="prop-1",
            room_id="room-1",
            name="Alex Tenant",
            email="alex@example.com",
            phone="+440000000000",
        )
        self.assertEqual(occupant.room_id, "room-1")
        self.assertEqual(occupant.email, "alex@example.com")
        self.assertEqual(occupant.phone, "+440000000000")


class EventTest(unittest.TestCase):
    def test_resource_type_is_event(self) -> None:
        event = SpireEvent(id="evt-1", device_id="dev-1", type=EventType.LEAK_DETECTED)
        self.assertEqual(event.resource_type, "Event")

    def test_carries_type_trait_and_value(self) -> None:
        event = SpireEvent(
            id="evt-1",
            device_id="dev-1",
            property_id="prop-1",
            type=EventType.STATE_CHANGE,
            trait=Trait.REPORTS_TEMPERATURE,
            value=21.5,
        )
        self.assertEqual(event.type, EventType.STATE_CHANGE)
        self.assertEqual(event.trait, Trait.REPORTS_TEMPERATURE)
        self.assertEqual(event.value, 21.5)

    def test_occurred_at_defaults_to_a_timestamp(self) -> None:
        event = SpireEvent(id="evt-1", device_id="dev-1", type=EventType.CAME_ONLINE)
        self.assertIsNotNone(event.occurred_at)


if __name__ == "__main__":
    unittest.main()
