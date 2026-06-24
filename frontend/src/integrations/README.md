# Frontend Integrations

Business logic, state management, and API clients for all vendor integrations.

## Overview

Each integration is self-contained in its own folder with:

- **types.ts** — TypeScript interfaces and types
- **hooks.ts** — React Query hooks for API communication
- **scan.ts** (optional) — Device discovery/scanning utilities
- **index.ts** — Barrel export for clean imports
- **README.md** — Implementation-specific docs

## Structure

```
integrations/
├── README.md (this file)
├── index.ts (barrel export)
├── bluetooth/
│   ├── README.md
│   ├── types.ts
│   ├── hooks.ts
│   ├── scan.ts
│   └── index.ts
├── govee/ (future)
│   ├── types.ts
│   ├── hooks.ts
│   └── index.ts
└── lifx/ (future)
    ├── types.ts
    ├── hooks.ts
    └── index.ts
```

## Usage

### Import from integration

```typescript
// ✅ Clean - use barrel exports
import {
  useBluetoothDevices,
  scanBluetoothDevices,
  type BluetoothDeviceOut,
} from "@/integrations/bluetooth";

// ❌ Avoid - importing from submodules
import { useBluetoothDevices } from "@/integrations/bluetooth/hooks";
```

### Using hooks in components

```typescript
function MyComponent() {
  const { data: devices } = useBluetoothDevices(propertyId);
  const { mutateAsync: pairDevice } = usePairBluetoothDevice();

  return (
    <div>
      {devices?.map(d => (
        <button key={d.id} onClick={() => pairDevice(...)}>
          {d.name}
        </button>
      ))}
    </div>
  );
}
```

## Adding a New Integration

1. **Create folder** → `integrations/[vendor]/`
2. **Create types.ts** → Define all request/response types
3. **Create hooks.ts** → useQuery/useMutation wrappers around API endpoints
4. **Create index.ts** → Export public API
5. **Create README.md** → Document implementation

Example: Adding Govee

```bash
mkdir -p integrations/govee
touch integrations/govee/{types,hooks,index,README}.ts
```

Then:

- Define types in `govee/types.ts`
- Implement hooks calling `/integrations/govee/*` endpoints
- Export from `integrations/index.ts`: `export * from "./govee"`

## Patterns

### React Query Cache Keys

Use integration name + resource type:

```typescript
const queryKey = ["bluetooth-devices", propertyId];
const queryKey = ["govee-lights"];
const queryKey = ["lifx-scenes"];
```

### Mutation Invalidation

Invalidate on success to keep UI in sync:

```typescript
onSuccess: () => {
  queryClient.invalidateQueries({ queryKey: ["bluetooth-devices"] });
};
```

### Error Handling

Let hooks return TanStack Query state (isLoading, error, data):

```typescript
const { data, isLoading, error } = useBluetoothDevices();

if (error) return <AlertCard message={error.message} />;
if (isLoading) return <Skeleton />;
return <DeviceList devices={data} />;
```

## Testing

Each integration should have:

- Hook tests in `frontend/tests/[vendor].test.tsx`
- Mock API responses via `vi.mock("@/lib/api/client")`
- Test loading, error, and success states

Run tests:

```bash
npm run test
```

## Related

- Backend: `backend/src/property/integrations/`
- Components: `src/components/integrations/`
- API Client: `src/lib/api/client.ts`
