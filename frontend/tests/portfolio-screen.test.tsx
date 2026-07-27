import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { PortfolioScreen } from "../src/components/portfolio/portfolio-screen";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    back: vi.fn(),
  }),
}));

vi.mock("@/lib/use-demo-mode", () => ({
  useDemoMode: () => ({
    demoMode: true,
    isHydrated: true,
    toggleDemoMode: vi.fn(),
  }),
}));

describe("PortfolioScreen", () => {
  it("renders the page header", () => {
    render(<PortfolioScreen />);
    // h1 is unique — tabs also say "Portfolios" so use role
    expect(screen.getByRole("heading", { name: "Portfolios" })).toBeDefined();
    expect(screen.getByText("Add property")).toBeDefined();
  });

  it("shows both portfolio sections in the Portfolios tab", () => {
    render(<PortfolioScreen />);
    expect(screen.getByText("Northern Portfolio")).toBeDefined();
    expect(screen.getByText("Southern Portfolio")).toBeDefined();
  });

  it("shows property names nested under their portfolios", () => {
    render(<PortfolioScreen />);
    expect(screen.getByText("Maple Court")).toBeDefined();
    expect(screen.getByText("Heron Place")).toBeDefined();
  });

  it("switches to All properties tab and shows filter chips", () => {
    render(<PortfolioScreen />);
    fireEvent.click(screen.getByText("All properties"));
    expect(screen.getByText("All")).toBeDefined();
    expect(screen.getByText("Clear")).toBeDefined();
    expect(screen.getByText("Attention")).toBeDefined();
    expect(screen.getByText("Critical")).toBeDefined();
  });

  it("filters to Attention shows only warn properties", () => {
    render(<PortfolioScreen />);
    fireEvent.click(screen.getByText("All properties"));
    fireEvent.click(screen.getByText("Attention"));
    // warn properties: Maple Court, Larkspur House
    expect(screen.getByText("Maple Court")).toBeDefined();
    expect(screen.getByText("Larkspur House")).toBeDefined();
    // alert property should be hidden
    expect(screen.queryByText("Northbrook Mill")).toBeNull();
  });

  it("filters to Critical shows only alert properties", () => {
    render(<PortfolioScreen />);
    fireEvent.click(screen.getByText("All properties"));
    fireEvent.click(screen.getByText("Critical"));
    expect(screen.getByText("Northbrook Mill")).toBeDefined();
    expect(screen.queryByText("Maple Court")).toBeNull();
  });

  it("toggles to list view and shows table headers", () => {
    render(<PortfolioScreen />);
    fireEvent.click(screen.getByText("All properties"));
    fireEvent.click(screen.getByText("list"));
    expect(screen.getByText("Property")).toBeDefined();
    expect(screen.getByText("Occupied")).toBeDefined();
    expect(screen.getByText("Type")).toBeDefined();
  });
});
