import type {
  Alert,
  AlphaconDevice,
  CommissionEvent,
  Insight,
  IntelligenceItem,
  MatterDeviceState,
  PowerHistoryPoint,
  Property,
  ProvisionEvent,
  Room,
  SavedDevice,
  ScannedDevice,
  ShellyDeviceState,
  StateHistoryEvent,
  VendorIntegration,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const TOKEN_STORAGE_KEY = "nestra_token";

function authHeader(): Record<string, string> {
  if (typeof window === "undefined") return {};
  const token = window.localStorage.getItem(TOKEN_STORAGE_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...authHeader(),
      ...init?.headers,
    },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface CurrentUser {
  id: string;
  email: string;
  full_name: string;
  organization: { id: string; name: string } | null;
}

export const authApi = {
  signup: (data: {
    email: string;
    password: string;
    full_name: string;
    organization_name?: string;
  }) =>
    apiFetch<TokenResponse>("/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  login: (data: { email: string; password: string }) =>
    apiFetch<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  me: () => apiFetch<CurrentUser>("/me"),
};

// ── Properties ────────────────────────────────────────────────────────────────

export const propertiesApi = {
  list: () => apiFetch<Property[]>("/api/v1/properties/"),
  get: (id: string) => apiFetch<Property>(`/api/v1/properties/${id}`),
  devices: (id: string) =>
    apiFetch<AlphaconDevice[]>(`/api/v1/properties/${id}/devices`),
  delete: (id: string) =>
    apiFetch<{ deleted: string }>(`/api/v1/properties/${id}`, {
      method: "DELETE",
    }),
};

// ── Rooms ─────────────────────────────────────────────────────────────────────

export const roomsApi = {
  list: (propertyId: string) =>
    apiFetch<Room[]>(`/api/v1/properties/${propertyId}/rooms`),
  create: (propertyId: string, data: { name: string; floor?: number }) =>
    apiFetch<Room>(`/api/v1/properties/${propertyId}/rooms`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  rename: (roomId: string, name: string) =>
    apiFetch<Room>(`/api/v1/rooms/${roomId}`, {
      method: "PATCH",
      body: JSON.stringify({ name }),
    }),
  delete: (roomId: string) =>
    apiFetch<{ deleted: string }>(`/api/v1/rooms/${roomId}`, {
      method: "DELETE",
    }),
};

// ── Devices ───────────────────────────────────────────────────────────────────

export const devicesApi = {
  list: () => apiFetch<AlphaconDevice[]>("/api/v1/devices/"),
  get: (id: string) => apiFetch<AlphaconDevice>(`/api/v1/devices/${id}`),
  assignRoom: (deviceId: string, roomId: string | null) =>
    apiFetch<SavedDevice>(`/api/v1/devices/${deviceId}`, {
      method: "PATCH",
      body: JSON.stringify({ room_id: roomId }),
    }),
};

// ── Alerts ────────────────────────────────────────────────────────────────────

export const alertsApi = {
  list: () => apiFetch<Alert[]>("/api/v1/alerts/"),
  dismiss: (id: string) =>
    apiFetch<void>(`/api/v1/alerts/${id}/dismiss`, { method: "PATCH" }),
};

// ── Insights ──────────────────────────────────────────────────────────────────

export const insightsApi = {
  get: (deviceId: string) => apiFetch<Insight>(`/api/v1/insights/${deviceId}`),
};

// ── Integrations ──────────────────────────────────────────────────────────────

export const integrationsApi = {
  list: () => apiFetch<VendorIntegration[]>("/api/v1/integrations/"),
  connect: (vendor: string, apiKey: string) =>
    apiFetch<{ vendor: string; status: string }>(
      `/api/v1/integrations/${vendor}/connect`,
      {
        method: "POST",
        body: JSON.stringify({ api_key: apiKey }),
      },
    ),
};

// ── Provisioning & device registry ───────────────────────────────────────────

export const provisioningApi = {
  hotspots: () => apiFetch<string[]>("/api/v1/integrations/hotspots"),
  scan: () => apiFetch<ScannedDevice[]>("/api/v1/integrations/scan"),
  listDevices: (propertyId?: string) => {
    const qs = propertyId
      ? `?property_id=${encodeURIComponent(propertyId)}`
      : "";
    return apiFetch<SavedDevice[]>(`/api/v1/integrations/devices${qs}`);
  },
  saveDevice: (data: {
    vendor: string;
    name: string;
    model: string;
    ip: string;
    mac: string;
    property_id: string;
    room_id?: string | null;
    vendor_id?: string;
  }) =>
    apiFetch<SavedDevice>("/api/v1/integrations/devices", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  deleteDevice: (id: string) =>
    apiFetch<void>(`/api/v1/integrations/devices/${id}`, { method: "DELETE" }),
  deleteDeviceById: (id: string) =>
    apiFetch<{ deleted: string }>(`/api/v1/devices/${id}`, {
      method: "DELETE",
    }),
  renameDevice: (id: string, name: string) =>
    apiFetch<SavedDevice>(`/api/v1/integrations/devices/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ name }),
    }),
  commissionMatter: (data: {
    setup_code: string;
    property_id: string;
    room_id: string;
  }) =>
    apiFetch<Record<string, unknown>>(
      "/api/v1/integrations/matter/commission",
      {
        method: "POST",
        body: JSON.stringify(data),
      },
    ),

  scanMatter: () =>
    apiFetch<{ devices: ScannedDevice[] }>(
      "/api/v1/integrations/scan/matter",
    ).then((data) => data.devices ?? []),
};

export async function streamProvision(
  payload: {
    hotspot_name: string;
    wifi_ssid: string;
    wifi_password: string;
    property_id: string;
    room_id?: string;
  },
  onEvent: (event: ProvisionEvent) => void,
): Promise<void> {
  const url = `${API_URL}/api/v1/integrations/provision`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.body) return;
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";
    for (const part of parts) {
      for (const line of part.split("\n")) {
        if (line.startsWith("data: ")) {
          try {
            onEvent(JSON.parse(line.slice(6)));
          } catch {
            // skip malformed event
          }
        }
      }
    }
  }
}

export async function streamCommissionMatter(
  payload: { setup_code: string; property_id: string; room_id: string },
  onEvent: (event: CommissionEvent) => void,
): Promise<void> {
  const url = `${API_URL}/api/v1/integrations/matter/commission`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.body) return;
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";
    for (const part of parts) {
      for (const line of part.split("\n")) {
        if (line.startsWith("data: ")) {
          try {
            onEvent(JSON.parse(line.slice(6)));
          } catch {
            // skip malformed event
          }
        }
      }
    }
  }
}

export const shellyDeviceApi = {
  control: (deviceId: string, command: "turn_on" | "turn_off") =>
    apiFetch<{ success: boolean; state: boolean }>(
      `/api/v1/devices/${deviceId}/control`,
      {
        method: "POST",
        body: JSON.stringify({ command }),
      },
    ),
  getState: (deviceId: string) =>
    apiFetch<ShellyDeviceState>(`/api/v1/devices/${deviceId}/state`),
  getHistory: (deviceId: string) =>
    apiFetch<StateHistoryEvent[]>(`/api/v1/devices/${deviceId}/history`),
  getPowerHistory: (deviceId: string) =>
    apiFetch<PowerHistoryPoint[]>(`/api/v1/devices/${deviceId}/power-history`),
};

// ── Agentic chat ──────────────────────────────────────────────────────────────

export async function streamChat(
  message: string,
  history: { role: string; content: string }[],
  onEvent: (event: { type: string; text?: string; message?: string }) => void,
): Promise<void> {
  const url = `${API_URL}/api/v1/chat/`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });
  if (!res.body) return;
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";
    for (const part of parts) {
      for (const line of part.split("\n")) {
        if (line.startsWith("data: ")) {
          try {
            onEvent(JSON.parse(line.slice(6)));
          } catch {
            // skip malformed event
          }
        }
      }
    }
  }
}

export const matterApi = {
  command: (deviceId: string, command: string, value: unknown) =>
    apiFetch<Record<string, unknown>>(
      `/api/v1/devices/matter/${deviceId}/command`,
      {
        method: "POST",
        body: JSON.stringify({ command, value }),
      },
    ),
  getState: (deviceId: string) =>
    apiFetch<MatterDeviceState>(`/api/v1/devices/matter/${deviceId}/state`),
};

// ── Intelligence ──────────────────────────────────────────────────────────────

export const intelligenceApi = {
  list: () => apiFetch<IntelligenceItem[]>("/api/v1/intelligence/"),
};
