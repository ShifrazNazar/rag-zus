import { useEffect, useState } from "react";
import { checkHealth } from "../services/api";
import { CheckCircle2, XCircle } from "lucide-react";

export default function BackendStatus() {
  const [isConnected, setIsConnected] = useState<boolean>(true);

  useEffect(() => {
    const checkConnection = async () => {
      try {
        setIsConnected(await checkHealth());
      } catch {
        setIsConnected(false);
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className={`flex items-center gap-2 text-xs ${
        isConnected ? "text-green-600" : "text-red-600"
      }`}
    >
      {isConnected ? (
        <CheckCircle2 className="h-3.5 w-3.5" />
      ) : (
        <XCircle className="h-3.5 w-3.5" />
      )}
      <span className="hidden sm:inline">
        {isConnected ? "Connected" : "Disconnected"}
      </span>
    </div>
  );
}
