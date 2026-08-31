"""Device enum persistence contract tests."""

import unittest

from sqlalchemy.dialects import postgresql

from property.domain import DeviceType
from property.repository.models import DeviceModel


class DeviceTypeEnumTest(unittest.TestCase):
    """Verify the ORM and PostgreSQL enum use the same values."""

    def test_device_type_uses_lowercase_domain_values(self) -> None:
        """Persist enum values accepted by the PostgreSQL devicetype type."""
        enum_type = DeviceModel.__table__.c.device_type.type
        processor = enum_type.bind_processor(postgresql.dialect())

        self.assertIsNotNone(processor)
        assert processor is not None
        self.assertEqual(processor(DeviceType.SENSOR), "sensor")
        self.assertEqual(processor(DeviceType.PLUG), "plug")
