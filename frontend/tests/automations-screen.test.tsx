import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { AutomationsScreen } from "../src/components/automations/automations-screen";

vi.mock("@/lib/use-demo-mode", () => ({
  useDemoMode: () => ({
    demoMode: true,
    isHydrated: true,
    toggleDemoMode: vi.fn(),
  }),
}));

describe("AutomationsScreen", () => {
  it("renders the page header", () => {
    render(<AutomationsScreen />);
    expect(
      screen.getByRole("heading", { name: "Agentic automations" }),
    ).toBeDefined();
    expect(screen.getByText("New automation")).toBeDefined();
  });

  it("renders the four stat cards", () => {
    render(<AutomationsScreen />);
    expect(screen.getByText("Active")).toBeDefined();
    expect(screen.getByText("Runs · 24h")).toBeDefined();
    expect(screen.getByText("New suggestions")).toBeDefined();
    // "Set by agent" appears in stat card + filter chip + automation tag
    expect(screen.getAllByText("Set by agent").length).toBeGreaterThanOrEqual(
      1,
    );
  });

  it("shows the agent suggestions panel", () => {
    render(<AutomationsScreen />);
    expect(
      screen.getByText("The agent wants to set up 3 automations"),
    ).toBeDefined();
    expect(screen.getByText("Weekday pre-arrival schedule")).toBeDefined();
    expect(screen.getByText("Quiet hours for Ash Cottage")).toBeDefined();
    expect(screen.getByText("Weekly leak check ping")).toBeDefined();
  });

  it("suggestion cards have approve, tweak and dismiss actions", () => {
    render(<AutomationsScreen />);
    expect(screen.getAllByText("Approve").length).toBe(3);
    expect(screen.getAllByText("Dismiss").length).toBe(3);
  });

  it("renders all live automations", () => {
    render(<AutomationsScreen />);
    expect(screen.getByText("Pre-arrival warm-up")).toBeDefined();
    expect(screen.getByText("Vacant cool-down")).toBeDefined();
    expect(screen.getByText("Frost protection")).toBeDefined();
    expect(screen.getByText("Daily energy summary")).toBeDefined();
  });

  it("Paused filter shows only disabled automations", () => {
    render(<AutomationsScreen />);
    fireEvent.click(screen.getByText("Paused"));
    expect(screen.getByText("Frost protection")).toBeDefined();
    expect(screen.queryByText("Pre-arrival warm-up")).toBeNull();
  });

  it("toggling an automation switch changes its enabled state", () => {
    render(<AutomationsScreen />);
    // Frost protection starts paused → one "Enable automation" button
    const enableBtns = screen.getAllByLabelText("Enable automation");
    expect(enableBtns.length).toBe(1);
    fireEvent.click(enableBtns[0]);
    // Now all are enabled → no Enable button remains
    expect(screen.queryAllByLabelText("Enable automation").length).toBe(0);
  });

  it("Manual filter shows only manual automations", () => {
    render(<AutomationsScreen />);
    // "Manual" also appears as a Tag on automation items — target the button
    fireEvent.click(screen.getByRole("button", { name: /^Manual/ }));
    expect(screen.getByText("Frost protection")).toBeDefined();
    expect(screen.queryByText("Pre-arrival warm-up")).toBeNull();
  });
});
