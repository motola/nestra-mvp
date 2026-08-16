import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { AutomationsScreen } from "../src/components/automations/automations-screen";

describe("AutomationsScreen", () => {
  it("renders empty state by default", () => {
    render(<AutomationsScreen />);
    expect(screen.getByRole("heading", { name: "Automations" })).toBeDefined();
    expect(screen.getByText("No automations created")).toBeDefined();
  });
});
