/**
 * Portfolio and Property API client
 */

export interface Portfolio {
  id: string;
  name: string;
  description: string;
  organization_id: string;
  is_default: boolean;
  created_at: string;
}

export interface Property {
  id: string;
  portfolio_id: string;
  organization_id: string;
  name: string;
  address: string;
  property_type: string;
  units: number;
  timezone: string;
  description?: string;
  created_at: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem("auth_token");
  if (!token) {
    throw new Error("No authentication token available. Please log in.");
  }
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export async function createPortfolio(data: {
  organization_id: string;
  name: string;
  description?: string;
}): Promise<Portfolio> {
  const response = await fetch(`${API_BASE}/portfolios`, {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to create portfolio: ${response.statusText}`);
  }

  return response.json();
}

export async function listPortfolios(
  organizationId: string,
): Promise<Portfolio[]> {
  const response = await fetch(
    `${API_BASE}/portfolios?organization_id=${organizationId}`,
    {
      headers: getAuthHeaders(),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch portfolios: ${response.statusText}`);
  }

  return response.json();
}

export async function getPortfolio(portfolioId: string): Promise<Portfolio> {
  const response = await fetch(`${API_BASE}/portfolios/${portfolioId}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch portfolio: ${response.statusText}`);
  }

  return response.json();
}

export async function createProperty(
  portfolioId: string,
  data: {
    organization_id: string;
    portfolio_id: string;
    name: string;
    address: string;
    property_type: string;
    units?: number;
    timezone?: string;
    description?: string;
  },
): Promise<Property> {
  const response = await fetch(
    `${API_BASE}/portfolios/${portfolioId}/properties`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
      },
      body: JSON.stringify(data),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to create property: ${response.statusText}`);
  }

  return response.json();
}

export async function listProperties(
  portfolioId: string,
  organizationId: string,
): Promise<Property[]> {
  const response = await fetch(
    `${API_BASE}/portfolios/${portfolioId}/properties?organization_id=${organizationId}`,
    {
      headers: getAuthHeaders(),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch properties: ${response.statusText}`);
  }

  return response.json();
}

export async function updatePortfolio(
  portfolioId: string,
  organizationId: string,
  data: {
    name: string;
    description?: string;
  },
): Promise<Portfolio> {
  const response = await fetch(
    `${API_BASE}/portfolios/${portfolioId}?organization_id=${organizationId}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
      },
      body: JSON.stringify(data),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to update portfolio: ${response.statusText}`);
  }

  return response.json();
}

export async function updateProperty(
  portfolioId: string,
  propertyId: string,
  organizationId: string,
  data: {
    name: string;
    address: string;
    property_type: string;
    units?: number;
    timezone?: string;
    description?: string;
  },
): Promise<Property> {
  const response = await fetch(
    `${API_BASE}/portfolios/${portfolioId}/properties/${propertyId}?organization_id=${organizationId}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
      },
      body: JSON.stringify(data),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to update property: ${response.statusText}`);
  }

  return response.json();
}
