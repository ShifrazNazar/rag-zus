const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string;
  tool_calls?: Array<{
    tool: string;
    input: Record<string, any>;
    output: Record<string, any>;
  }>;
  intent?: string;
}

export interface ChatRequest {
  message: string;
  history?: ChatMessage[];
}

export interface ChatResponse {
  response: string;
  tool_calls?: Array<{
    tool: string;
    input: Record<string, any>;
    output: Record<string, any>;
  }>;
  intent?: string;
  memory?: Record<string, any>;
}

export interface CalculatorRequest {
  expression: string;
}

export interface CalculatorResponse {
  result: number | null;
  error: string | null;
}

export interface ProductsResponse {
  results: Array<{
    name: string;
    description: string;
    price?: string;
    url?: string;
  }>;
  summary?: string;
}

export interface OutletsResponse {
  results: Array<{
    id: number;
    name: string;
    location: string;
    district?: string;
    hours?: string;
    services?: string;
    lat?: number;
    lon?: number;
  }>;
  sql_query?: string;
}

export async function sendMessage(
  message: string,
  history: ChatMessage[] = []
): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        history,
      }),
    });

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ detail: "Unknown error" }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error sending message:", error);
    throw error;
  }
}

export async function calculate(
  expression: string
): Promise<CalculatorResponse> {
  try {
    const response = await fetch(`${API_URL}/calculate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ expression }),
    });

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ error: "Unknown error" }));
      throw new Error(error.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error calculating:", error);
    throw error;
  }
}

export async function searchProducts(query: string): Promise<ProductsResponse> {
  try {
    const response = await fetch(
      `${API_URL}/products?query=${encodeURIComponent(query)}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ detail: "Unknown error" }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error searching products:", error);
    throw error;
  }
}

export async function searchOutlets(query: string): Promise<OutletsResponse> {
  try {
    const response = await fetch(
      `${API_URL}/outlets?query=${encodeURIComponent(query)}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ detail: "Unknown error" }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error searching outlets:", error);
    throw error;
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`);
    return response.ok;
  } catch (error) {
    console.error("Health check failed:", error);
    return false;
  }
}
