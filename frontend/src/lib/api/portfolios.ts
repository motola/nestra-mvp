/**
 * Portfolio and Property API client
 */

export interface Portfolio {
  id: string;
  name: string;
  description: string;
  organization_id: string;
  created_at: string;
}

export interface Property {
  id: string;
  portfolio_id: string;
  name: string;
  address: string;
  property_type: string;
  units: number;
  timezone: string;
  created_at: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function createPortfolio(data: {
  organization_id: string;
  name: string;
  description?: string;
}): Promise<Portfolio> {
  const response = await fetch(`${API_BASE}/portfolios`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
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
      headers: {
        Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
      },
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
      headers: {
        Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
      },
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch properties: ${response.statusText}`);
  }

  return response.json();
}
