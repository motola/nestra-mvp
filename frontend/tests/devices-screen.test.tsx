import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DevicesScreen } from "../src/components/devices/devices-screen";

vi.mock("@/lib/use-demo-mode", () => ({
  useDemoMode: () => ({
    demoMode: true,
    isHydrated: true,
    toggleDemoMode: vi.fn(),
  }),
}));

describe("DevicesScreen", () => {
  it("renders the page header", () => {
    render(<DevicesScreen />);
    expect(screen.getByRole("heading", { name: "Devices" })).toBeDefined();
    expect(screen.getByText("Pair device")).toBeDefined();
  });

  it("renders the four stat cards", () => {
    render(<DevicesScreen />);
    expect(screen.getByText("Total devices")).toBeDefined();
    expect(screen.getByText("Online")).toBeDefined();
    expect(screen.getByText("Categories")).toBeDefined();
    // "Unreachable" appears in both stat card and filter chip — just check count
    expect(screen.getAllByText("Unreachable").length).toBeGreaterThanOrEqual(1);
  });

  it("shows device rows in the table", () => {
    render(<DevicesScreen />);
    expect(screen.getByText("Living thermostat")).toBeDefined();
    expect(screen.getByText("Front lock")).toBeDefined();
    expect(screen.getByText("Energy meter")).toBeDefined();
  });

  it("Needs attention filter shows only alerting devices", () => {
    render(<DevicesScreen />);
    fireEvent.click(screen.getByText("Needs attention"));
    expect(screen.getByText("Living thermostat")).toBeDefined();
    expect(screen.getByText("Hallway motion")).toBeDefined();
    expect(screen.queryByText("Front lock")).toBeNull();
  });

  it("Unreachable filter shows only offline devices", () => {
    render(<DevicesScreen />);
    // Target the filter chip by role — the span/label uses the same text
    fireEvent.click(screen.getByRole("button", { name: /Unreachable/ }));
    expect(screen.getAllByText("Hallway motion").length).toBeGreaterThanOrEqual(
      1,
    );
    expect(screen.queryByText("Living thermostat")).toBeNull();
  });

  it("clicking a device row opens the device drawer", () => {
    render(<DevicesScreen />);
    fireEvent.click(screen.getByText("Front lock"));
    expect(screen.getByText("current state")).toBeDefined();
    expect(screen.getByText("Activity")).toBeDefined();
  });

  it("closing the drawer removes it", () => {
    render(<DevicesScreen />);
    fireEvent.click(screen.getByText("Front lock"));
    fireEvent.click(screen.getByLabelText("Close device drawer"));
    expect(screen.queryByText("current state")).toBeNull();
  });

  it("shows the vendor sync info card", () => {
    render(<DevicesScreen />);
    expect(
      screen.getByText("Devices stay in sync with your vendors"),
    ).toBeDefined();
  });
});
