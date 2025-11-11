/**
 * BackendStatus component to show backend connection status.
 */
import { useEffect, useState } from "react";
import { checkHealth } from "../services/api";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { cn } from "../lib/utils";

export default function BackendStatus() {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const checkConnection = async () => {
      setIsChecking(true);
      try {
        const healthy = await checkHealth();
        setIsConnected(healthy);
      } catch {
        setIsConnected(false);
      } finally {
        setIsChecking(false);
      }
    };

    checkConnection();
    // Check every 30 seconds
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  if (isChecking) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 text-xs text-muted-foreground">
        <Loader2 className="h-3 w-3 animate-spin" />
        <span>Checking backend...</span>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex items-center gap-2 px-4 py-2 text-xs",
        isConnected
          ? "text-green-600 dark:text-green-400"
          : "text-red-600 dark:text-red-400"
      )}
    >
      {isConnected ? (
        <>
          <CheckCircle2 className="h-3 w-3" />
          <span>Backend connected</span>
        </>
      ) : (
        <>
          <XCircle className="h-3 w-3" />
          <span>Backend disconnected</span>
        </>
      )}
    </div>
  );
}

