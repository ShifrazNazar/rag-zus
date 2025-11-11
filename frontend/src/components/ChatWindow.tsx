/**
 * ChatWindow component - main chat interface container.
 */
import { useChat } from "../hooks/useChat";
import MessageList from "./MessageList";
import InputComposer from "./InputComposer";
import QuickActions from "./QuickActions";
import BackendStatus from "./BackendStatus";
import { Alert, AlertDescription } from "./ui/alert";
import { Card, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "./ui/button";

export default function ChatWindow() {
  const { messages, isLoading, error, sendMessage, clearChat } = useChat();

  const handleSend = async (message: string) => {
    // Handle reset command
    if (
      message.toLowerCase().trim() === "reset" ||
      message.toLowerCase().trim() === "/reset"
    ) {
      clearChat();
      return;
    }

    await sendMessage(message);
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <Card className="rounded-none border-x-0 border-t-0 shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle>Mindhive AI Chatbot</CardTitle>
          <CardDescription>
            Multi-agent chatbot with RAG, Text2SQL, and tool calling
          </CardDescription>
        </CardHeader>
        <BackendStatus />
      </Card>

      {/* Quick Actions */}
      <QuickActions onAction={handleSend} disabled={isLoading} />

      {/* Error Banner */}
      {error && (
        <Alert variant="destructive" className="m-4 border-destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="flex items-center justify-between">
            <span>{error}</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => window.location.reload()}
              className="ml-2"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Reload
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Message List */}
      <div className="flex-1 overflow-hidden">
        <MessageList messages={messages} isLoading={isLoading} />
      </div>

      {/* Input Composer */}
      <InputComposer onSend={handleSend} disabled={isLoading} />
    </div>
  );
}
