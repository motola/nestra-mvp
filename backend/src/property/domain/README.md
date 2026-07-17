# Property Domain

Core domain models for properties and devices — the "rules" of smart home management.

## Models

### Device

Unified smart home device schema across all integrations (no per-vendor variants).

```python
class Device(BaseModel):
    id: UUID | None
    organization_id: UUID
    property_id: UUID
    integration_id: UUID
    device_type: DeviceType
    vendor: str                  # "august", "bluetooth", "govee", etc
    vendor_specific_id: str      # vendor's device ID
    vendor_name: str | None      # friendly name from vendor
    online: bool
    last_sync: datetime
    created_at: datetime
    updated_at: datetime
    raw_state: dict[str, object] # vendor-specific metadata
```

**Key principles:**

- Single schema for all vendors (no `DeviceLock`, `DeviceCamera`, etc)
- Vendor-specific data in `raw_state` dict
- Frozen=False allows state updates during sync

### DeviceType (StrEnum)

Canonical device types:

```python
class DeviceType(StrEnum):
    LOCK = "lock"
    THERMOSTAT = "thermostat"
    CAMERA = "camera"
    PLUG = "plug"
    SENSOR = "sensor"
    SPEAKER = "speaker"
```

Used for:

- Filtering devices by type
- Determining available control commands
- Type-safe enum (prevents typos)

## Design Notes

### Why Single Schema?

1. **Simpler APIs** — One endpoint returns all devices, no type-specific queries
2. **Vendor agnostic** — Control commands work the same way regardless of vendor
3. **Less code** — No duplication across device types
4. **Flexible** — New vendor types added without schema changes

### raw_state Dict

Stores vendor-specific data (brightness level, battery %, mode, etc) without polluting the canonical schema.

Example August lock:

```python
device.raw_state = {
    "model": "August Pro",
    "battery_level": 95,
    "lock_status": "locked",
    "connected_via": "wifi",
}
```

Example Bluetooth light:

```python
device.raw_state = {
    "rssi": -45,
    "battery_level": 85,
    "brightness": 75,
    "color_temp": 4000,
}
```

## Related

- Property module: `backend/src/property/README.md`
- Integrations (normalize payloads to Device): `backend/src/integrations/README.md`
- Repository (persist Device): `backend/src/property/repository/README.md`
- Intelligence (query Device for control): `backend/src/intelligence/README.md`
