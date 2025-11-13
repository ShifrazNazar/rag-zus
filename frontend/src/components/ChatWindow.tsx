import { useChat } from "../hooks/useChat";
import MessageList from "./MessageList";
import InputComposer from "./InputComposer";
import QuickActions from "./QuickActions";
import BackendStatus from "./BackendStatus";
import { Alert, AlertDescription } from "./ui/alert";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "./ui/button";

export default function ChatWindow() {
  const { messages, isLoading, error, sendMessage, clearChat } = useChat();

  const handleSend = async (message: string) => {
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
    <div className="flex flex-col h-screen bg-gradient-to-br from-background to-muted/20">
      <div className="border-b border-border/50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold tracking-tight">
                Mindhive AI Chatbot
              </h1>
              <p className="text-sm text-muted-foreground mt-0.5">
                Multi-agent chatbot with RAG, Text2SQL, and tool calling
              </p>
            </div>
            <BackendStatus />
          </div>
        </div>
      </div>

      <div className="border-b border-border/50 bg-muted/30">
        <div className="max-w-4xl mx-auto px-4">
          <QuickActions onAction={handleSend} disabled={isLoading} />
        </div>
      </div>

      {error && (
        <div className="max-w-4xl mx-auto w-full px-4 pt-4">
          <Alert variant="destructive" className="border-destructive/50">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="flex items-center justify-between">
              <span>{error}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => window.location.reload()}
                className="ml-2 h-7"
              >
                <RefreshCw className="h-3 w-3 mr-1.5" />
                Reload
              </Button>
            </AlertDescription>
          </Alert>
        </div>
      )}

      <div className="flex-1 overflow-hidden min-h-0">
        <div className="max-w-4xl mx-auto h-full flex flex-col">
          <MessageList messages={messages} isLoading={isLoading} />
        </div>
      </div>

      <div className="border-t border-border/50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-4xl mx-auto">
          <InputComposer onSend={handleSend} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}
