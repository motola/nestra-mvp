import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { IntelligenceWorkspace } from "../src/components/intelligence/intelligence-workspace";

describe("IntelligenceWorkspace", () => {
  it("renders all seed chat tabs", () => {
    render(<IntelligenceWorkspace />);
    expect(screen.getByText("Energy spend this week")).toBeDefined();
    expect(screen.getByText("Northbrook hub restart")).toBeDefined();
    expect(screen.getByText("Maple Court vacancy options")).toBeDefined();
  });

  it("shows the empty state by default (new chat is active)", () => {
    render(<IntelligenceWorkspace />);
    expect(screen.getByText("What would you like to do?")).toBeDefined();
    expect(screen.getByText(/Hello Marcus/i)).toBeDefined();
  });

  it("shows the transcript when switching to a seed chat with messages", () => {
    render(<IntelligenceWorkspace />);
    fireEvent.click(screen.getByText("Energy spend this week"));
    expect(
      screen.getByText(/energy spend this week and where did most/i),
    ).toBeDefined();
    expect(screen.getByText(/312 kWh last week/)).toBeDefined();
  });

  it("adds a new empty tab when New chat is clicked", () => {
    render(<IntelligenceWorkspace />);
    // "New chat" button is a primary Button, tabs have role="tab"
    const beforeCount = screen.getAllByRole("tab").length;
    // Use role="button" to target the header "New chat" button, not the tab
    fireEvent.click(screen.getByRole("button", { name: "New chat" }));
    const afterCount = screen.getAllByRole("tab").length;
    expect(afterCount).toBe(beforeCount + 1);
  });

  it("sends a message and shows it in the transcript", () => {
    render(<IntelligenceWorkspace />);
    const input = screen.getByLabelText("Message Alphacon AI");
    fireEvent.change(input, { target: { value: "How many vacant units?" } });
    fireEvent.keyDown(input, { key: "Enter" });
    // The AI canned reply is unique to the transcript
    expect(screen.getByText(/Maple Court Flat 3B \+ Flat 1A/)).toBeDefined();
  });

  it("clears the input after sending", () => {
    render(<IntelligenceWorkspace />);
    const input = screen.getByLabelText(
      "Message Alphacon AI",
    ) as HTMLInputElement;
    fireEvent.change(input, { target: { value: "Test message" } });
    fireEvent.keyDown(input, { key: "Enter" });
    expect(input.value).toBe("");
  });

  it("opens the quick actions tray when Quick actions is clicked", () => {
    render(<IntelligenceWorkspace />);
    fireEvent.click(screen.getByLabelText("Quick actions"));
    // "Waiting for my approval" only exists inside the tray, not in any tab title
    expect(screen.getByText("Waiting for my approval")).toBeDefined();
    expect(screen.getByText("Devices offline")).toBeDefined();
  });

  it("shows the inline answer when a quick action tile is picked", () => {
    render(<IntelligenceWorkspace />);
    fireEvent.click(screen.getByLabelText("Quick actions"));
    fireEvent.click(screen.getByText("Vacant units right now"));
    expect(screen.getByText(/Maple Court Flat 3B/)).toBeDefined();
  });

  it("opens the activity drawer when Recent activity is clicked", () => {
    render(<IntelligenceWorkspace />);
    fireEvent.click(screen.getByLabelText("Recent activity"));
    expect(screen.getByText("Recent activity")).toBeDefined();
    expect(
      screen.getByText("Turned off heating in Maple Court Flat 3B"),
    ).toBeDefined();
  });

  it("closes the activity drawer when the close button is clicked", () => {
    render(<IntelligenceWorkspace />);
    fireEvent.click(screen.getByLabelText("Recent activity"));
    fireEvent.click(screen.getByLabelText("Close activity drawer"));
    expect(
      screen.queryByText("Turned off heating in Maple Court Flat 3B"),
    ).toBeNull();
  });
});
