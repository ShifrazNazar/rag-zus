import { useChat } from "../hooks/useChat";
import MessageList from "./MessageList";
import InputComposer from "./InputComposer";
import QuickActions from "./QuickActions";

export default function ChatWindow() {
  const { messages, isLoading, sendMessage, clearChat } = useChat();

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
    <div className="flex flex-col h-screen bg-gradient-to-br from-[#F5F1EB] via-background to-[#F0E8DC]">
      <div className="border-b border-border/40 bg-gradient-to-r from-[#F5F1EB] to-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-5">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full"></div>
              <div className="relative w-10 h-10 bg-primary rounded-lg flex items-center justify-center transform rotate-[-55deg]">
                <span className="text-primary-foreground font-bold text-xl">
                  Z
                </span>
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
                ZUS Coffee Assistant
              </h1>
              <p className="text-sm text-muted-foreground mt-0.5">
                Your personal coffee shop guide • Find outlets, products & more
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="border-b border-border/40 bg-gradient-to-r from-accent/30 via-muted/20 to-accent/30">
        <div className="max-w-4xl mx-auto px-4">
          <QuickActions onAction={handleSend} disabled={isLoading} />
        </div>
      </div>

      <div className="flex-1 overflow-hidden min-h-0">
        <div className="max-w-4xl mx-auto h-full flex flex-col">
          <MessageList messages={messages} isLoading={isLoading} />
        </div>
      </div>

      <div className="border-t border-border/40 bg-gradient-to-r from-background/95 via-[#F5F1EB]/90 to-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <InputComposer onSend={handleSend} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}
