/**
 * Access control and audit API client
 */

import { getToken } from "@/lib/auth/session";

export interface AccessGrant {
  id: string;
  device_id: string;
  grantee_user_id?: string;
  grantee_email?: string;
  access_type: "read" | "control" | "manage";
  capabilities: string[];
  expires_at?: string;
  created_at: string;
  updated_at: string;
  revoked_at?: string;
}

export interface ShareLink {
  id: string;
  device_id: string;
  access_type: "read" | "control";
  created_at: string;
  claimed_at?: string;
  expires_at: string;
  revoked_at?: string;
}

export interface AuditEvent {
  id: string;
  organization_id: string;
  actor_user_id?: string;
  actor_type: "user" | "system" | "automation";
  action: string;
  resource_type: string;
  resource_id: string;
  resource_name?: string;
  changes: Record<string, unknown>;
  status: "success" | "failure";
  reason?: string;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
}

export interface AuditEventList {
  items: AuditEvent[];
  total: number;
  skip: number;
  limit: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Access Grants
export async function grantDeviceAccess(
  deviceId: string,
  data: {
    grantee_user_id?: string;
    grantee_email?: string;
    access_type: "read" | "control" | "manage";
    capabilities?: string[];
    expires_at?: string;
  },
): Promise<AccessGrant> {
  const response = await fetch(
    `${API_BASE}/access/devices/${deviceId}/access-grants`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify(data),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to grant access: ${response.statusText}`);
  }

  return response.json();
}

export async function listAccessGrants(
  deviceId: string,
  skip?: number,
  limit?: number,
): Promise<Array<AccessGrant>> {
  const params = new URLSearchParams({
    ...(skip !== undefined && { skip: String(skip) }),
    ...(limit !== undefined && { limit: String(limit) }),
  });

  const response = await fetch(
    `${API_BASE}/access/devices/${deviceId}/access-grants?${params}`,
    {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch access grants: ${response.statusText}`);
  }

  return response.json();
}

export async function revokeAccess(grantId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/access/access-grants/${grantId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to revoke access: ${response.statusText}`);
  }
}

export async function getMyDevices(
  skip?: number,
  limit?: number,
): Promise<Array<{ id: string; name: string; vendor: string }>> {
  const params = new URLSearchParams({
    ...(skip !== undefined && { skip: String(skip) }),
    ...(limit !== undefined && { limit: String(limit) }),
  });

  const response = await fetch(`${API_BASE}/access/my-devices?${params}`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!response.ok) {
    throw new Error(
      `Failed to fetch accessible devices: ${response.statusText}`,
    );
  }

  return response.json();
}

// Share Links
export async function createShareLink(
  deviceId: string,
  data: {
    access_type: "read" | "control";
    expires_at?: string;
  },
): Promise<ShareLink & { token: string }> {
  const response = await fetch(
    `${API_BASE}/access/devices/${deviceId}/share-links`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify(data),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to create share link: ${response.statusText}`);
  }

  return response.json();
}

export async function listShareLinks(
  deviceId: string,
  skip?: number,
  limit?: number,
): Promise<Array<ShareLink>> {
  const params = new URLSearchParams({
    ...(skip !== undefined && { skip: String(skip) }),
    ...(limit !== undefined && { limit: String(limit) }),
  });

  const response = await fetch(
    `${API_BASE}/access/devices/${deviceId}/share-links?${params}`,
    {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch share links: ${response.statusText}`);
  }

  return response.json();
}

export async function claimShareLink(
  token: string,
  userId: string,
): Promise<ShareLink> {
  const response = await fetch(
    `${API_BASE}/access/share-links/${token}/claim`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify({ user_id: userId }),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to claim share link: ${response.statusText}`);
  }

  return response.json();
}

// Audit Log
export async function listAuditEvents(
  organizationId: string,
  filters?: {
    action?: string;
    resource_type?: string;
    start_date?: string;
    end_date?: string;
    skip?: number;
    limit?: number;
  },
): Promise<AuditEventList> {
  const params = new URLSearchParams({
    organization_id: organizationId,
    ...(filters?.action && { action: filters.action }),
    ...(filters?.resource_type && { resource_type: filters.resource_type }),
    ...(filters?.start_date && { start_date: filters.start_date }),
    ...(filters?.end_date && { end_date: filters.end_date }),
    ...(filters?.skip !== undefined && { skip: String(filters.skip) }),
    ...(filters?.limit !== undefined && { limit: String(filters.limit) }),
  });

  const response = await fetch(`${API_BASE}/access/audit/events?${params}`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch audit events: ${response.statusText}`);
  }

  return response.json();
}

export async function getAuditEvent(
  eventId: string,
  organizationId: string,
): Promise<AuditEvent> {
  const params = new URLSearchParams({ organization_id: organizationId });
  const response = await fetch(
    `${API_BASE}/access/audit/events/${eventId}?${params}`,
    {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch audit event: ${response.statusText}`);
  }

  return response.json();
}

export async function getAuditSummary(organizationId: string): Promise<{
  total_events: number;
  events_today: number;
  action_counts: Record<string, number>;
}> {
  const response = await fetch(
    `${API_BASE}/access/audit/summary?organization_id=${organizationId}`,
    {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch audit summary: ${response.statusText}`);
  }

  return response.json();
}

export async function getDeviceAuditLog(
  deviceId: string,
  organizationId: string,
  skip?: number,
  limit?: number,
): Promise<AuditEventList> {
  const params = new URLSearchParams({
    organization_id: organizationId,
    ...(skip !== undefined && { skip: String(skip) }),
    ...(limit !== undefined && { limit: String(limit) }),
  });

  const response = await fetch(
    `${API_BASE}/access/audit/events/device/${deviceId}?${params}`,
    {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch device audit log: ${response.statusText}`);
  }

  return response.json();
}
