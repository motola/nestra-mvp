/**
 * Occupancy management API client
 */

import { getToken } from "@/lib/auth/session";

export interface Tenant {
  id: string;
  organization_id: string;
  user_id?: string;
  full_name: string;
  email: string;
  phone?: string;
  tenant_type: "RESIDENT" | "GUEST" | "STAFF";
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

export interface Room {
  id: string;
  property_id: string;
  name: string;
  room_type: string;
  floor_number?: number;
  square_feet?: number;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Stay {
  id: string;
  property_id: string;
  check_in_date: string;
  check_out_date?: string;
  status: "active" | "completed" | "cancelled";
  notes?: string;
  created_at: string;
  updated_at: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Tenants
export async function createTenant(data: {
  organization_id: string;
  full_name: string;
  email: string;
  phone?: string;
  tenant_type?: string;
}): Promise<Tenant> {
  const response = await fetch(`${API_BASE}/occupancy/tenants`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to create tenant: ${response.statusText}`);
  }

  return response.json();
}

export async function listTenants(
  organizationId: string,
  skip?: number,
  limit?: number,
): Promise<Array<Tenant>> {
  const params = new URLSearchParams({
    organization_id: organizationId,
    ...(skip !== undefined && { skip: String(skip) }),
    ...(limit !== undefined && { limit: String(limit) }),
  });

  const response = await fetch(`${API_BASE}/occupancy/tenants?${params}`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch tenants: ${response.statusText}`);
  }

  return response.json();
}

export async function getTenant(tenantId: string): Promise<Tenant> {
  const response = await fetch(`${API_BASE}/occupancy/tenants/${tenantId}`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch tenant: ${response.statusText}`);
  }

  return response.json();
}

export async function updateTenant(
  tenantId: string,
  data: {
    full_name?: string;
    email?: string;
    phone?: string;
  },
): Promise<Tenant> {
  const response = await fetch(`${API_BASE}/occupancy/tenants/${tenantId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to update tenant: ${response.statusText}`);
  }

  return response.json();
}

export async function deleteTenant(tenantId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/occupancy/tenants/${tenantId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to delete tenant: ${response.statusText}`);
  }
}

// Rooms
export async function createRoom(data: {
  property_id: string;
  name: string;
  room_type: string;
  floor_number?: number;
  square_feet?: number;
  description?: string;
}): Promise<Room> {
  const response = await fetch(`${API_BASE}/occupancy/rooms`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to create room: ${response.statusText}`);
  }

  return response.json();
}

export async function listRooms(
  propertyId: string,
  skip?: number,
  limit?: number,
): Promise<Array<Room>> {
  const params = new URLSearchParams({
    property_id: propertyId,
    ...(skip !== undefined && { skip: String(skip) }),
    ...(limit !== undefined && { limit: String(limit) }),
  });

  const response = await fetch(`${API_BASE}/occupancy/rooms?${params}`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch rooms: ${response.statusText}`);
  }

  return response.json();
}

// Stays
export async function createStay(data: {
  property_id: string;
  check_in_date: string;
  check_out_date?: string;
  room_ids?: string[];
  tenant_ids?: string[];
}): Promise<Stay> {
  const response = await fetch(`${API_BASE}/occupancy/stays`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to create stay: ${response.statusText}`);
  }

  return response.json();
}

export async function listStays(
  propertyId: string,
  skip?: number,
  limit?: number,
): Promise<Array<Stay>> {
  const params = new URLSearchParams({
    property_id: propertyId,
    ...(skip !== undefined && { skip: String(skip) }),
    ...(limit !== undefined && { limit: String(limit) }),
  });

  const response = await fetch(`${API_BASE}/occupancy/stays?${params}`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch stays: ${response.statusText}`);
  }

  return response.json();
}

export async function getStay(stayId: string): Promise<Stay> {
  const response = await fetch(`${API_BASE}/occupancy/stays/${stayId}`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch stay: ${response.statusText}`);
  }

  return response.json();
}

export async function updateStay(
  stayId: string,
  data: {
    check_out_date?: string;
    status?: string;
  },
): Promise<Stay> {
  const response = await fetch(`${API_BASE}/occupancy/stays/${stayId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to update stay: ${response.statusText}`);
  }

  return response.json();
}
