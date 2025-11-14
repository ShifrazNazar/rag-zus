import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import InputComposer from "../InputComposer";

describe("InputComposer", () => {
  it("renders input field", () => {
    const onSend = vi.fn();
    render(<InputComposer onSend={onSend} />);
    expect(
      screen.getByPlaceholderText(/ask about outlets/i)
    ).toBeInTheDocument();
  });

  it("calls onSend when send button is clicked", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<InputComposer onSend={onSend} />);

    const input = screen.getByPlaceholderText(/ask about outlets/i);
    const sendButton = screen.getByRole("button", { name: /send message/i });

    await user.type(input, "Hello");
    await user.click(sendButton);

    expect(onSend).toHaveBeenCalledWith("Hello");
  });

  it("calls onSend when Enter is pressed", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<InputComposer onSend={onSend} />);

    const input = screen.getByPlaceholderText(/ask about outlets/i);
    await user.type(input, "Test message{Enter}");

    expect(onSend).toHaveBeenCalledWith("Test message");
  });

  it("does not send empty messages", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<InputComposer onSend={onSend} />);

    const sendButton = screen.getByRole("button", { name: /send message/i });
    await user.click(sendButton);

    expect(onSend).not.toHaveBeenCalled();
  });

  it("disables input when disabled prop is true", () => {
    const onSend = vi.fn();
    render(<InputComposer onSend={onSend} disabled={true} />);

    const input = screen.getByPlaceholderText(/ask about outlets/i);
    expect(input).toBeDisabled();
  });

  it("matches snapshot", () => {
    const onSend = vi.fn();
    const { container } = render(<InputComposer onSend={onSend} />);
    expect(container).toMatchSnapshot();
  });

  it("matches snapshot when disabled", () => {
    const onSend = vi.fn();
    const { container } = render(
      <InputComposer onSend={onSend} disabled={true} />
    );
    expect(container).toMatchSnapshot();
  });
});
