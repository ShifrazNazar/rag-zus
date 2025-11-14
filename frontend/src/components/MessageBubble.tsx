import type { ChatMessage } from "../services/api";
import { User, Bot } from "lucide-react";

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
    <div
      className={`flex mb-5 gap-3 ${isUser ? "justify-end" : "justify-start"}`}
    >
      {!isUser && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center border border-primary/20">
            <Bot className="h-4 w-4 text-primary" />
          </div>
        </div>
      )}
      <div
        className={`flex flex-col ${
          isUser ? "items-end" : "items-start"
        } max-w-[85%]`}
      >
        <div
          className={`rounded-xl px-4 py-3 shadow-sm ${
            isUser
              ? "bg-primary text-primary-foreground shadow-primary/20"
              : "bg-card border border-border/60 text-card-foreground shadow-sm"
          }`}
        >
          <div className="text-sm whitespace-pre-wrap break-words leading-relaxed">
            {message.content}
          </div>
        </div>
        {message.timestamp && (
          <div
            className={`text-xs mt-1.5 px-1 ${
              isUser ? "text-right" : "text-left"
            } ${isUser ? "opacity-70" : "opacity-60"}`}
          >
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
        )}
      </div>
      {isUser && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
            <User className="h-4 w-4 text-primary-foreground" />
          </div>
        </div>
      )}
    </div>
  );
}
