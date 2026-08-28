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

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    back: vi.fn(),
  }),
}));

describe("DevicesScreen", () => {
  it("renders full ui structure with zero data when no devices", () => {
    render(<DevicesScreen />);
    expect(screen.getByRole("heading", { name: "Devices" })).toBeDefined();
    expect(screen.getByText("Total devices")).toBeDefined();
    expect(screen.getByText("Online")).toBeDefined();
    expect(screen.getByText("Categories")).toBeDefined();
    expect(screen.getByText("All devices")).toBeDefined();
    expect(screen.getByText("All")).toBeDefined();
    expect(screen.getByText("Needs attention")).toBeDefined();
  });
});
