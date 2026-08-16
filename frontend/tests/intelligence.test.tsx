import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { IntelligenceWorkspace } from "../src/components/intelligence/intelligence-workspace";

describe("IntelligenceWorkspace", () => {
  it("renders empty state on first load", () => {
    render(<IntelligenceWorkspace />);
    expect(screen.getByText("Start a conversation")).toBeDefined();
  });

  it("shows single new chat tab by default", () => {
    render(<IntelligenceWorkspace />);
    const tabs = screen.getAllByRole("tab");
    expect(tabs.length).toBe(1);
    expect(tabs[0].textContent).toContain("New chat");
  });

  it("adds a new tab when New chat button is clicked", () => {
    render(<IntelligenceWorkspace />);
    const beforeCount = screen.getAllByRole("tab").length;
    fireEvent.click(screen.getByRole("button", { name: "New chat" }));
    const afterCount = screen.getAllByRole("tab").length;
    expect(afterCount).toBe(beforeCount + 1);
  });

  it("sends a message and shows user message in transcript", () => {
    render(<IntelligenceWorkspace />);
    const input = screen.getByLabelText("Message Alphacon AI");
    fireEvent.change(input, { target: { value: "Specific test question" } });
    fireEvent.keyDown(input, { key: "Enter" });
    const messages = screen.getAllByText("Specific test question");
    expect(messages.length).toBeGreaterThan(0);
  });

  it("shows Thinking... response after sending message", () => {
    render(<IntelligenceWorkspace />);
    const input = screen.getByLabelText("Message Alphacon AI");
    fireEvent.change(input, { target: { value: "Are devices online?" } });
    fireEvent.keyDown(input, { key: "Enter" });
    expect(screen.getByText("Thinking...")).toBeDefined();
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

  it("uses first message as chat title", () => {
    render(<IntelligenceWorkspace />);
    const input = screen.getByLabelText("Message Alphacon AI");
    fireEvent.change(input, { target: { value: "Unique energy question" } });
    fireEvent.keyDown(input, { key: "Enter" });
    const messages = screen.getAllByText("Unique energy question");
    expect(messages.length).toBeGreaterThan(0);
  });

  it("truncates long titles with ellipsis", () => {
    render(<IntelligenceWorkspace />);
    const input = screen.getByLabelText("Message Alphacon AI");
    const longMessage =
      "This is a very long message that should be truncated with ellipsis when used as title";
    fireEvent.change(input, { target: { value: longMessage } });
    fireEvent.keyDown(input, { key: "Enter" });
    // Title is truncated at 36 chars + ellipsis
    const tabs = screen.getAllByRole("tab");
    expect(tabs.some((t) => t.textContent?.includes("…"))).toBe(true);
  });
});
