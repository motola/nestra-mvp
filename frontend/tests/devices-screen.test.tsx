import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { DevicesScreen } from "../src/components/devices/devices-screen";
import { PropertyProvider } from "../src/lib/property/provider";

vi.mock("@/lib/use-devices", () => ({
  useDevices: () => ({
    devices: [],
    loading: false,
    error: null,
  }),
}));

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
  listPortfolios: () => Promise.resolve([]),
  listProperties: () => Promise.resolve([]),
}));

describe("DevicesScreen", () => {
  it("renders full ui structure with zero data when no devices", () => {
    render(
      <PropertyProvider>
        <DevicesScreen />
      </PropertyProvider>,
    );
    expect(screen.getByRole("heading", { name: "Devices" })).toBeDefined();
    expect(screen.getByText("Total devices")).toBeDefined();
    expect(screen.getByText("Online")).toBeDefined();
    expect(screen.getByText("Categories")).toBeDefined();
    expect(screen.getByText("All devices")).toBeDefined();
    expect(screen.getByText("All")).toBeDefined();
    expect(screen.getByText("Needs attention")).toBeDefined();
  });
});
