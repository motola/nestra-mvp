import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { DevicesScreen } from "../src/components/devices/devices-screen";

vi.mock("@/lib/use-devices", () => ({
  useDevices: () => ({
    devices: [],
    loading: false,
    error: null,
  }),
}));

describe("DevicesScreen", () => {
  it("renders empty state when no devices", () => {
    render(<DevicesScreen />);
    expect(screen.getByRole("heading", { name: "Devices" })).toBeDefined();
    expect(screen.getByText("No devices connected")).toBeDefined();
  });
});
