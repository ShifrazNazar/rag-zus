/**
 * localStorage utility for chat persistence.
 */

const CHAT_HISTORY_KEY = 'mindhive_chat_history';
const MAX_HISTORY_LENGTH = 50;

export interface StoredMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

/**
 * Save chat history to localStorage.
 */
export function saveChatHistory(messages: StoredMessage[]): void {
  try {
    // Keep only last N messages
    const messagesToSave = messages.slice(-MAX_HISTORY_LENGTH);
    localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(messagesToSave));
  } catch (error) {
    console.error('Error saving chat history:', error);
    // localStorage might be full or disabled
  }
}

/**
 * Load chat history from localStorage.
 */
export function loadChatHistory(): StoredMessage[] {
  try {
    const stored = localStorage.getItem(CHAT_HISTORY_KEY);
    if (!stored) {
      return [];
    }
    const messages = JSON.parse(stored) as StoredMessage[];
    return Array.isArray(messages) ? messages : [];
  } catch (error) {
    console.error('Error loading chat history:', error);
    return [];
  }
}

/**
 * Clear chat history from localStorage.
 */
export function clearChatHistory(): void {
  try {
    localStorage.removeItem(CHAT_HISTORY_KEY);
  } catch (error) {
    console.error('Error clearing chat history:', error);
  }
}

/**
 * Get chat history size.
 */
export function getChatHistorySize(): number {
  try {
    const stored = localStorage.getItem(CHAT_HISTORY_KEY);
    return stored ? JSON.parse(stored).length : 0;
  } catch (error) {
    return 0;
  }
}

