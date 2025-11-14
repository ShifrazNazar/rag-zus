import type { ChatMessage } from "../services/api";

interface MessageBubbleProps {
  message: ChatMessage;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  if (isSystem) {
    return (
      <div className="flex justify-center my-2">
        <span className="text-xs text-muted-foreground bg-muted px-3 py-1 rounded-full">
          {message.content}
        </span>
      </div>
    );
  }

  return (
    <div className={`flex mb-5 ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-xl px-4 py-3 shadow-sm ${
          isUser
            ? "bg-primary text-primary-foreground shadow-primary/20"
            : "bg-card border border-border/60 text-card-foreground shadow-sm"
        }`}
      >
        <div className="text-sm whitespace-pre-wrap break-words leading-relaxed">
          {message.content}
        </div>
        {message.timestamp && (
          <div className={`text-xs mt-2 ${isUser ? "opacity-80" : "opacity-60"}`}>
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
        )}
      </div>
    </div>
  );
}
