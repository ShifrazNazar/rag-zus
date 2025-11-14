import { useState, useRef } from "react";
import type { KeyboardEvent } from "react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Send } from "lucide-react";

interface InputComposerProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

const QUICK_ACTIONS = ["/calc", "/products", "/outlets", "/reset"];

export default function InputComposer({
  onSend,
  disabled = false,
}: InputComposerProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message);
      setMessage("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const showAutocomplete = message.trim().startsWith("/");
  const filteredActions = QUICK_ACTIONS.filter((action) => {
    const messageLower = message.trim().toLowerCase();
    const actionLower = action.toLowerCase();
    return messageLower === "/" || actionLower.includes(messageLower.slice(1));
  });

  return (
    <div className="p-4">
      <div className="flex items-end gap-2">
        <div className="flex-1 relative">
          <Textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about outlets, products, or calculations... (Enter to send, Shift+Enter for newline, / to see quick actions)"
            disabled={disabled}
            rows={1}
            className="resize-none min-h-[52px] max-h-[120px] border-border/60 focus:border-primary/50 focus:ring-primary/20"
          />
          {showAutocomplete && filteredActions.length > 0 && (
            <div className="absolute bottom-full left-0 right-0 mb-2 bg-popover border border-border/60 rounded-xl shadow-lg z-10 overflow-hidden">
              {filteredActions.map((action) => (
                <div
                  key={action}
                  className="px-3 py-2 cursor-pointer text-sm hover:bg-accent/50 transition-colors"
                  onClick={() => {
                    setMessage(action + " ");
                    textareaRef.current?.focus();
                  }}
                >
                  {action}
                </div>
              ))}
            </div>
          )}
        </div>
        <Button
          onClick={handleSend}
          disabled={!message.trim() || disabled}
          size="icon"
          className="h-[52px] w-[52px]"
          aria-label="Send message"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
