# Bluetooth Integration

Quick reference for the Bluetooth device pairing feature.

## Overview

Allows users to discover and pair Bluetooth smart home devices through the web interface.

**Status:** ✅ Complete (NEM-23)
**API:** `POST /integrations/bluetooth/pair`, `POST /integrations/bluetooth/unpair`, `GET /integrations/bluetooth/devices`

## Files

- **`bluetooth-pairing-modal.tsx`** — Modal component for device discovery and pairing
- **`integrations-screen.tsx`** — Main integrations screen (includes Bluetooth UI)
- **`../../../lib/api/hooks/use-bluetooth.ts`** — React hooks + Web Bluetooth API wrapper

## User Flow

1. User navigates to Integrations → Catalog
2. Clicks "Pair" on Bluetooth vendor card
3. Modal opens, user clicks "Scan Devices"
4. Browser prompts for Bluetooth permission
5. User selects device from discovered list
6. Device paired and appears in Connected tab

## Testing

### Manual (Localhost)
```bash
# Terminal 1: Backend
cd backend && python -m uvicorn src.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev

# Browser: http://localhost:3000
# Login: test@example.com / password123
# Navigate: Integrations → Catalog → Bluetooth → Pair
```

### Unit Tests
```bash
# Backend (8 tests)
cd backend && make test

# Frontend (5 tests)
cd frontend && npm run test
```

## API Endpoints

### Pair Device
```
POST /integrations/bluetooth/pair
{
  "mac_address": "AA:BB:CC:DD:EE:FF",
  "name": "Device Name",
  "property_id": "uuid",
  "device_type": "light",
  "rssi": -45,
  "battery_level": 85
}
```

### Unpair Device
```
POST /integrations/bluetooth/unpair?device_id=uuid
```

### List Devices
```
GET /integrations/bluetooth/devices?property_id=uuid (optional filter)
```

## React Hooks

### useBluetoothDevices(propertyId?)
Fetch paired devices.
```typescript
const { data: devices } = useBluetoothDevices(propertyId);
```

### usePairBluetoothDevice()
Pair a new device.
```typescript
const { mutateAsync } = usePairBluetoothDevice();
await mutateAsync({ mac_address, name, property_id, ... });
```

### useUnpairBluetoothDevice()
Unpair a device.
```typescript
const { mutateAsync } = useUnpairBluetoothDevice();
await mutateAsync(deviceId);
```

### scanBluetoothDevices()
Scan for nearby devices.
```typescript
const devices = await scanBluetoothDevices();
// Returns: Array<{ name, mac_address }>
```

## Browser Support

- ✅ Chrome 56+
- ✅ Edge 79+
- ⚠️ Firefox (disabled by default)
- ⚠️ Safari (limited iOS support)

## Component State Machine

```
initial → scanning → selecting → pairing → success/error
```

### States
- **initial:** Shows scan button
- **scanning:** Loading indicator + status message
- **selecting:** Device list for user to choose from
- **pairing:** Pairing in progress
- **success:** Success message, closes after 1.5s
- **error:** Error message with retry button

## Data Structure

```typescript
interface BluetoothDeviceOut {
  id: string;
  property_id: string;
  mac_address: string;        // AA:BB:CC:DD:EE:FF
  name: string;               // "Living Room Light"
  device_type: string;        // "light", "sensor", etc
  rssi: number;               // Signal strength (-100 to -20)
  battery_level: number | null; // 0-100, or null
  is_paired: boolean;
  last_sync: string;          // ISO 8601 timestamp
  created_at: string;         // ISO 8601 timestamp
}
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| "Web Bluetooth not supported" | Browser doesn't support API | Use Chrome/Edge |
| Scan times out | No devices nearby | Turn on a Bluetooth device |
| "Device already paired" (409) | MAC already in DB | Use different device |
| Modal closes | Network error | Check backend logs |

## Future Work

- Phase 2: Device control (read/write characteristics)
- Phase 3: Real-time state sync
- Phase 4: Extend pattern to other vendors (Govee, Lifx, Nest)

## Related

- Backend: `backend/src/property/api/routes.py`
- Backend tests: `backend/tests/property/test_bluetooth.py`
- Frontend tests: `frontend/tests/bluetooth-pairing.test.tsx`
- Full docs: `docs/BLUETOOTH_INTEGRATION.md`
