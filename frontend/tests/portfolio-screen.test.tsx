import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { PortfolioScreen } from "../src/components/portfolio/portfolio-screen";
import { PropertyProvider } from "../src/lib/property/provider";
import { listPortfolios, listProperties } from "../src/lib/api/portfolios";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    back: vi.fn(),
  }),
}));

vi.mock("@/lib/auth/provider", () => ({
  useAuth: () => ({
    user: { id: "user-1", email: "dev@example.com", full_name: "Dev User" },
    organization: { id: "org-1", name: "Org", slug: "org" },
    isLoading: false,
    isAuthenticated: true,
    setSession: vi.fn(),
    clearSession: vi.fn(),
  }),
}));

vi.mock("@/lib/api/portfolios", () => ({
  listPortfolios: vi.fn(),
  listProperties: vi.fn(),
  createPortfolio: vi.fn(),
}));

function renderScreen() {
  return render(
    <PropertyProvider>
      <PortfolioScreen />
    </PropertyProvider>,
  );
}

describe("PortfolioScreen", () => {
  beforeEach(() => {
    vi.mocked(listPortfolios).mockReset();
    vi.mocked(listProperties).mockReset();
  });

  it("renders the empty state when the organization has no portfolios", async () => {
    vi.mocked(listPortfolios).mockResolvedValue([]);

    renderScreen();

    expect(screen.getByRole("heading", { name: "Portfolios" })).toBeDefined();
    expect(screen.getByText("Add portfolio")).toBeDefined();
    expect(await screen.findByText("No portfolios yet")).toBeDefined();
    expect(listPortfolios).toHaveBeenCalledWith("org-1");
  });

  it("renders portfolios with counts aggregated from their properties", async () => {
    vi.mocked(listPortfolios).mockResolvedValue([
      {
        id: "pf-1",
        name: "North Region",
        description: "Manchester",
        organization_id: "org-1",
        is_default: true,
        created_at: "2026-01-01T00:00:00Z",
      },
    ]);
    vi.mocked(listProperties).mockResolvedValue([
      {
        id: "prop-1",
        portfolio_id: "pf-1",
        organization_id: "org-1",
        name: "Maple Court",
        address: "1 Maple St",
        property_type: "MIXED_USE",
        units: 12,
        timezone: "Europe/London",
        created_at: "2026-01-01T00:00:00Z",
      },
      {
        id: "prop-2",
        portfolio_id: "pf-1",
        organization_id: "org-1",
        name: "Oak House",
        address: "2 Oak Rd",
        property_type: "LONG_TERM_RENTAL",
        units: 8,
        timezone: "Europe/London",
        created_at: "2026-01-01T00:00:00Z",
      },
    ]);

    renderScreen();

    expect(await screen.findByText("North Region")).toBeDefined();
    expect(listProperties).toHaveBeenCalledWith("pf-1", "org-1");

    await waitFor(() => {
      expect(
        screen.getByText("2 properties · 20 units · 0 devices"),
      ).toBeDefined();
    });
  });
});
