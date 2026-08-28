import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { IntegrationsScreen } from "../src/components/integrations/integrations-screen";
import { PropertyProvider } from "../src/lib/property/provider";
import { AuthProvider } from "../src/lib/auth/provider";

vi.mock("@/lib/api/portfolios", () => ({
  listPortfolios: vi.fn(() => Promise.resolve([])),
  listProperties: vi.fn(() => Promise.resolve([])),
}));

vi.mock("next/navigation", () => ({
  useSearchParams: () => null,
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

describe("IntegrationsScreen", () => {
  it("renders empty state by default", () => {
    render(
      <AuthProvider>
        <PropertyProvider>
          <IntegrationsScreen />
        </PropertyProvider>
      </AuthProvider>,
    );
    expect(screen.getByRole("heading", { name: "Integrations" })).toBeDefined();
    expect(screen.getByText("No connections yet")).toBeDefined();
  });
});
