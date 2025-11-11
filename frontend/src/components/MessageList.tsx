/**
 * MessageList component for displaying the chat message list.
 */
import { useEffect, useRef } from "react";
import type { ChatMessage } from "../services/api";
import MessageBubble from "./MessageBubble";
import { Card, CardContent } from "./ui/card";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-2">
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-muted-foreground">
          <Card className="max-w-md">
            <CardContent className="pt-6 text-center">
              <p className="text-lg font-medium mb-2">
                Welcome to Mindhive Chatbot!
              </p>
              <p className="text-sm text-muted-foreground">
                I can help you with calculations, product searches, and finding
                outlets.
              </p>
              <p className="text-sm text-muted-foreground mt-2">
                Try asking me something!
              </p>
            </CardContent>
          </Card>
        </div>
      ) : (
        <>
          {messages.map((message, index) => (
            <MessageBubble key={index} message={message} />
          ))}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-muted rounded-lg px-4 py-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                  <div
                    className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                    style={{ animationDelay: "0.1s" }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
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
