import { useEffect, useRef } from "react";
import type { ChatMessage } from "../services/api";
import MessageBubble from "./MessageBubble";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 min-h-0">
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
          <div className="mb-4 opacity-40">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center transform rotate-[-55deg]">
              <span className="text-primary/30 font-bold text-3xl">Z</span>
            </div>
          </div>
          <p className="text-base">Start a conversation...</p>
          <p className="text-sm mt-1 opacity-70">Ask about outlets, products, or calculations</p>
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {messages.map((message, index) => {
              // Show conversation threading - group consecutive messages from same role
              const prevMessage = index > 0 ? messages[index - 1] : null;
              const isNewThread = !prevMessage || prevMessage.role !== message.role;
              
              return (
                <div key={index} className={isNewThread && index > 0 ? "mt-6" : ""}>
                  <MessageBubble message={message} />
                </div>
              );
            })}
          </div>
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-card border border-border/60 rounded-xl px-4 py-3 shadow-sm">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce"></div>
                  <div
                    className="w-2 h-2 bg-primary/60 rounded-full animate-bounce"
                    style={{ animationDelay: "0.15s" }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-primary/60 rounded-full animate-bounce"
                    style={{ animationDelay: "0.3s" }}
                  ></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  );
}
