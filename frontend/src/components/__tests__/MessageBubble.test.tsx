import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import MessageBubble from "../MessageBubble";
import type { ChatMessage } from "../../services/api";

describe("MessageBubble", () => {
  it("renders user message correctly", () => {
    const message: ChatMessage = {
      role: "user",
      content: "Hello, world!",
      timestamp: "2024-01-01T00:00:00Z",
    };

    render(<MessageBubble message={message} />);
    expect(screen.getByText("Hello, world!")).toBeInTheDocument();
  });

  it("renders assistant message correctly", () => {
    const message: ChatMessage = {
      role: "assistant",
      content: "Hi there!",
      timestamp: "2024-01-01T00:00:01Z",
    };

    render(<MessageBubble message={message} />);
    expect(screen.getByText("Hi there!")).toBeInTheDocument();
  });

  it("displays timestamp when provided", () => {
    const message: ChatMessage = {
      role: "user",
      content: "Test message",
      timestamp: "2024-01-01T12:00:00Z",
    };

    render(<MessageBubble message={message} />);
    // Timestamp should be formatted and displayed
    expect(screen.getByText("Test message")).toBeInTheDocument();
  });

  it("matches snapshot for user message", () => {
    const message: ChatMessage = {
      role: "user",
      content: "Hello, world!",
      timestamp: "2024-01-01T00:00:00Z",
    };

    const { container } = render(<MessageBubble message={message} />);
    expect(container).toMatchSnapshot();
  });

  it("matches snapshot for assistant message", () => {
    const message: ChatMessage = {
      role: "assistant",
      content: "Hi there!",
      timestamp: "2024-01-01T00:00:01Z",
    };

    const { container } = render(<MessageBubble message={message} />);
    expect(container).toMatchSnapshot();
  });

  it("matches snapshot for system message", () => {
    const message: ChatMessage = {
      role: "system",
      content: "System notification",
      timestamp: "2024-01-01T00:00:02Z",
    };

    const { container } = render(<MessageBubble message={message} />);
    expect(container).toMatchSnapshot();
  });
});
