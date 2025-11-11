/**
 * Custom hook for chat state management.
 */
import { useState, useEffect, useCallback } from 'react';
import { sendMessage, ChatMessage, ChatResponse } from '../services/api';
import { saveChatHistory, loadChatHistory, clearChatHistory } from '../utils/localStorage';

export interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (message: string) => Promise<void>;
  clearChat: () => void;
  retryLastMessage: () => Promise<void>;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastMessage, setLastMessage] = useState<string | null>(null);

  // Load chat history on mount
  useEffect(() => {
    const savedHistory = loadChatHistory();
    if (savedHistory.length > 0) {
      setMessages(savedHistory);
    }
  }, []);

  // Save chat history whenever messages change
  useEffect(() => {
    if (messages.length > 0) {
      saveChatHistory(messages);
    }
  }, [messages]);

  const handleSendMessage = useCallback(async (message: string) => {
    if (!message.trim() || isLoading) {
      return;
    }

    const userMessage: ChatMessage = {
      role: 'user',
      content: message.trim(),
      timestamp: new Date().toISOString(),
    };

    // Add user message immediately
    setMessages((prev) => [...prev, userMessage]);
    setLastMessage(message);
    setIsLoading(true);
    setError(null);

    try {
      // Get current history for context
      const currentHistory = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp,
      }));

      // Send message to backend
      const response: ChatResponse = await sendMessage(message, currentHistory);

      // Add assistant response
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      
      // Add error message to chat
      const errorChatMessage: ChatMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorChatMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [messages, isLoading]);

  const handleClearChat = useCallback(() => {
    setMessages([]);
    setError(null);
    clearChatHistory();
  }, []);

  const handleRetryLastMessage = useCallback(async () => {
    if (lastMessage) {
      // Remove last user and assistant messages
      setMessages((prev) => {
        const filtered = [...prev];
        // Remove last assistant message if exists
        if (filtered.length > 0 && filtered[filtered.length - 1].role === 'assistant') {
          filtered.pop();
        }
        // Remove last user message
        if (filtered.length > 0 && filtered[filtered.length - 1].role === 'user') {
          filtered.pop();
        }
        return filtered;
      });
      
      // Resend the message
      await handleSendMessage(lastMessage);
    }
  }, [lastMessage, handleSendMessage]);

  return {
    messages,
    isLoading,
    error,
    sendMessage: handleSendMessage,
    clearChat: handleClearChat,
    retryLastMessage: handleRetryLastMessage,
  };
}

