import { useState, useEffect, useCallback } from "react";
import { sendMessage } from "../services/api";
import type { ChatMessage, ChatResponse } from "../services/api";
import {
  saveChatHistory,
  loadChatHistory,
  clearChatHistory,
} from "../utils/localStorage";

export interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (message: string) => Promise<void>;
  clearChat: () => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const savedHistory = loadChatHistory();
    if (savedHistory.length > 0) {
      const chatMessages: ChatMessage[] = savedHistory.map((msg) => ({
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp,
      }));
      setMessages(chatMessages);
    }
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      const storedMessages = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp || new Date().toISOString(),
      }));
      saveChatHistory(storedMessages);
    }
  }, [messages]);

  const handleSendMessage = useCallback(
    async (message: string) => {
      if (!message.trim() || isLoading) {
        return;
      }

      const userMessage: ChatMessage = {
        role: "user",
        content: message.trim(),
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        const recentMessages = messages.slice(-20);
        const currentHistory = recentMessages.map((msg) => ({
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp,
        }));

        const response: ChatResponse = await sendMessage(
          message,
          currentHistory
        );

        const assistantMessage: ChatMessage = {
          role: "assistant",
          content: response.response,
          timestamp: new Date().toISOString(),
          ...(response.tool_calls && { tool_calls: response.tool_calls }),
          ...(response.intent && { intent: response.intent }),
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to send message";
        setError(errorMessage);

        const errorChatMessage: ChatMessage = {
          role: "assistant",
          content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errorChatMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [messages, isLoading]
  );

  const handleClearChat = useCallback(() => {
    setMessages([]);
    setError(null);
    clearChatHistory();
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage: handleSendMessage,
    clearChat: handleClearChat,
  };
}
