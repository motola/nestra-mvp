/**
 * Device management API client
 */

import { getToken } from "@/lib/auth/session";

export interface Device {
  id: string;
  organization_id: string;
  portfolio_id: string;
  property_id: string;
  integration_id: string;
  vendor: string;
  vendor_name: string;
  device_type: string;
  online: boolean;
  category?: string;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  created_at: string;
  updated_at: string;
}

export interface DeviceDetail extends Device {
  placement?: {
    id: string;
    property_id: string;
    room_id?: string;
    created_at: string;
    updated_at: string;
  };
  integrations?: Array<{
    id: string;
    integration_id: string;
    connection_identifier: string;
    last_synced_at?: string;
  }>;
  capabilities?: Array<{
    id: string;
    code: string;
    name: string;
    category: string;
  }>;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function createBluetoothDevice(data: {
  integration_id: string;
  property_id: string;
  name: string;
  mac_address: string;
  room_id?: string;
}): Promise<Device> {
  const token = getToken();
  const response = await fetch(
    `${API_BASE}/integrations/${data.integration_id}/devices/bluetooth`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        property_id: data.property_id,
        name: data.name,
        mac_address: data.mac_address,
        room_id: data.room_id,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(
      `Failed to create Bluetooth device: ${response.statusText}`,
    );
  }

  const result = await response.json();
  return Array.isArray(result) ? result[0] : result;
}

export async function createShellyDevice(data: {
  integration_id: string;
  property_id: string;
  name: string;
  device_id: string;
  ip_address: string;
  room_id?: string;
}): Promise<Device> {
  const token = getToken();
  const response = await fetch(
    `${API_BASE}/integrations/${data.integration_id}/devices/shelly`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        property_id: data.property_id,
        name: data.name,
        device_id: data.device_id,
        ip_address: data.ip_address,
        room_id: data.room_id,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to create Shelly device: ${response.statusText}`);
  }

  const result = await response.json();
  return Array.isArray(result) ? result[0] : result;
}

export async function getDevice(deviceId: string): Promise<DeviceDetail> {
  const response = await fetch(`${API_BASE}/devices/${deviceId}`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch device: ${response.statusText}`);
  }

  return response.json();
}

export async function controlDevice(
  deviceId: string,
  data: {
    organization_id: string;
    command: string;
    params?: Record<string, unknown>;
  },
): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_BASE}/devices/${deviceId}/control`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to control device: ${response.statusText}`);
  }

  return response.json();
}

export async function getPropertyDevices(
  propertyId: string,
): Promise<Device[]> {
  const response = await fetch(`${API_BASE}/properties/${propertyId}/devices`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch property devices: ${response.statusText}`);
  }

  return response.json();
}
