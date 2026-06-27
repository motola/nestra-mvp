"""SPIRE — Smart Property Interoperability REsources.

The open-source canonical model for smart-property devices: vendor-agnostic
resources, a trait vocabulary, and (over time) the adapter contract that
integrations implement. This package has no dependency on the host application
or any vendor, so it can stand alone.

Public API::

    from spire import SpireDevice, Trait, derive_traits
"""

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
from spire.traits import Trait, derive_traits

__all__ = [
    "AuditMeta",
    "Connectivity",
    "DeviceCategory",
    "DeviceIdentity",
    "DeviceNaming",
    "DevicePlacement",
    "DeviceStatus",
    "SpireDevice",
    "SpireIdentifier",
    "Trait",
    "VendorRef",
    "derive_traits",
]
