# Bluetooth Integration (Frontend)

React hooks and utilities for discovering and managing Bluetooth smart home devices.

## Overview

Provides type-safe wrappers around the Bluetooth API endpoints:

- **Hooks** — TanStack Query wrappers for device queries and mutations
- **Scanning** — Web Bluetooth API integration for device discovery
- **Types** — Shared TypeScript interfaces for type safety

## Files

| File        | Purpose                                                               |
| ----------- | --------------------------------------------------------------------- |
| `types.ts`  | Bluetooth device types and interfaces                                 |
| `hooks.ts`  | useBluetoothDevices, usePairBluetoothDevice, useUnpairBluetoothDevice |
| `scan.ts`   | scanBluetoothDevices Web Bluetooth API utility                        |
| `index.ts`  | Barrel export (public API)                                            |
| `README.md` | This file                                                             |

## Hooks

### useBluetoothDevices(propertyId?: string)

Fetch paired Bluetooth devices, optionally filtered by property.

```typescript
const { data: devices = [], isLoading, error } = useBluetoothDevices(propertyId);

if (error) return <Error message={error.message} />;
if (isLoading) return <Skeleton />;
return <DeviceList devices={devices} />;
```

**Cache Key:** `["bluetooth-devices", propertyId]`

---

### usePairBluetoothDevice()

Pair a discovered device to a property.

```typescript
const { mutateAsync, isPending, error } = usePairBluetoothDevice();

try {
  const response = await mutateAsync({
    mac_address: "AA:BB:CC:DD:EE:FF",
    name: "Device Name",
    property_id: propertyId,
    device_type: "light",
    rssi: -45,
    battery_level: 85,
  });
  console.log("Paired:", response.device_id);
} catch (err) {
  console.error("Pairing failed:", err.message);
}
```

**On Success:** Invalidates `["bluetooth-devices"]` query (all properties)

---

### useUnpairBluetoothDevice()

Unpair a Bluetooth device.

```typescript
const { mutateAsync, isPending } = useUnpairBluetoothDevice();

await mutateAsync(deviceId);
```

**On Success:** Invalidates `["bluetooth-devices"]` query

---

## Utilities

### scanBluetoothDevices()

Scan for nearby Bluetooth devices using Web Bluetooth API.

```typescript
try {
  const devices = await scanBluetoothDevices();
  // devices: Array<{ name: string; mac_address: string }>

  for (const device of devices) {
    await mutateAsync({
      mac_address: device.mac_address,
      name: device.name,
      property_id,
    });
  }
} catch (error) {
  if (error.name === "NotFoundError") {
    console.log("User cancelled scan");
  } else {
    console.error("Scan failed:", error.message);
  }
}
```

**Throws:**

- `Error` if Web Bluetooth API not supported
- `DOMException` (NotFoundError) if user cancels

**Browser Support:**

- ✅ Chrome 56+
- ✅ Edge 79+
- ⚠️ Firefox (disabled by default, enable `dom.bluetooth.enabled`)
- ⚠️ Safari (limited iOS support)

## Types

```typescript
interface BluetoothDeviceOut {
  id: string;
  property_id: string;
  mac_address: string; // AA:BB:CC:DD:EE:FF
  name: string;
  device_type: string; // "light", "sensor", etc
  rssi: number; // Signal strength (-100 to -20 dBm)
  battery_level: number | null; // 0-100 or null
  is_paired: boolean;
  last_sync: string; // ISO 8601
  created_at: string; // ISO 8601
}

interface BluetoothDeviceIn {
  mac_address: string;
  name: string;
  property_id: string;
  device_type?: string; // Default: "unknown"
  rssi?: number; // Default: -100
  battery_level?: number | null;
}

interface BluetoothPairResponse {
  device_id: string;
  status: string; // "paired"
  message: string;
}

interface ScannedDevice {
  name: string;
  mac_address: string;
}
```

## Usage in Components

### Basic Device List

```typescript
import { useBluetoothDevices } from "@/integrations/bluetooth";

function DeviceList({ propertyId }: { propertyId: string }) {
  const { data: devices = [] } = useBluetoothDevices(propertyId);

  return (
    <ul>
      {devices.map(d => (
        <li key={d.id}>{d.name} ({d.mac_address})</li>
      ))}
    </ul>
  );
}
```

### Pairing Flow

```typescript
import {
  scanBluetoothDevices,
  usePairBluetoothDevice
} from "@/integrations/bluetooth";

function PairingModal({ propertyId, onSuccess }: Props) {
  const [devices, setDevices] = useState<ScannedDevice[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const { mutateAsync: pairDevice } = usePairBluetoothDevice();

  const handleScan = async () => {
    setIsScanning(true);
    try {
      const found = await scanBluetoothDevices();
      setDevices(found);
    } catch (error) {
      alert(`Scan failed: ${error.message}`);
    } finally {
      setIsScanning(false);
    }
  };

  const handlePair = async (device: ScannedDevice) => {
    try {
      await pairDevice({
        mac_address: device.mac_address,
        name: device.name,
        property_id: propertyId,
      });
      onSuccess();
    } catch (error) {
      alert(`Pairing failed: ${error.message}`);
    }
  };

  return (
    <div>
      <button onClick={handleScan} disabled={isScanning}>
        {isScanning ? "Scanning..." : "Scan Devices"}
      </button>
      {devices.map(d => (
        <button key={d.mac_address} onClick={() => handlePair(d)}>
          {d.name}
        </button>
      ))}
    </div>
  );
}
```

## Testing

Tests in `frontend/tests/bluetooth-pairing.test.tsx`:

```bash
npm run test
```

**What's tested:**

- Initial modal state rendering
- Scanning state and loader
- Device list display
- Error handling and recovery
- Modal lifecycle (open → scan → select → pair → success)

Mock navigator.bluetooth for testing:

```typescript
Object.defineProperty(navigator, "bluetooth", {
  value: { requestDevice: vi.fn() },
  configurable: true,
});
```

## Future Enhancements

- **Real device control** — Read/write Bluetooth characteristics
- **Multiple device scanning** — Currently returns single device (Web Bluetooth API limitation)
- **Device pairing state** — Track which devices support pairing vs connection
- **Signal strength UI** — Visual RSSI indicator
- **Battery status widget** — Show low battery warnings
- **Offline state sync** — Recover from network failures

## Related

- Backend: `backend/src/integrations/bluetooth/`
- Components: `src/components/integrations/`
- Integrations Overview: `src/integrations/README.md`
