import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { PortfolioScreen } from "../src/components/portfolio/portfolio-screen";
import { PropertyProvider } from "../src/lib/property/provider";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    back: vi.fn(),
  }),
}));

describe("PortfolioScreen", () => {
  it("renders the page header and empty state", () => {
    render(
      <PropertyProvider>
        <PortfolioScreen />
      </PropertyProvider>,
    );
    expect(screen.getByRole("heading", { name: "Portfolios" })).toBeDefined();
    expect(screen.getByText("Add portfolio")).toBeDefined();
    expect(screen.getByText("No portfolios yet")).toBeDefined();
  });
});
