const CHAT_HISTORY_KEY = "mindhive_chat_history";
const MAX_HISTORY_LENGTH = 50;

export interface StoredMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
}

export function saveChatHistory(messages: StoredMessage[]): void {
  try {
    const messagesToSave = messages.slice(-MAX_HISTORY_LENGTH);
    localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(messagesToSave));
  } catch (error) {
    console.error("Error saving chat history:", error);
  }
}

export function loadChatHistory(): StoredMessage[] {
  try {
    const stored = localStorage.getItem(CHAT_HISTORY_KEY);
    if (!stored) {
      return [];
    }
    const messages = JSON.parse(stored) as StoredMessage[];
    return Array.isArray(messages) ? messages : [];
  } catch (error) {
    console.error("Error loading chat history:", error);
    return [];
  }
}

export function clearChatHistory(): void {
  try {
    localStorage.removeItem(CHAT_HISTORY_KEY);
  } catch (error) {
    console.error("Error clearing chat history:", error);
  }
}
