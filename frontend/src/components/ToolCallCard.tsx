import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Calculator, ShoppingBag, MapPin, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import { cn } from "../lib/utils";

interface ToolCall {
  tool: string;
  input: Record<string, any>;
  output: {
    success: boolean;
    result?: any;
    error?: string;
  };
}

interface ToolCallCardProps {
  toolCall: ToolCall;
}

const toolIcons: Record<string, React.ReactNode> = {
  calculator: <Calculator className="h-4 w-4" />,
  products: <ShoppingBag className="h-4 w-4" />,
  outlets: <MapPin className="h-4 w-4" />,
};

const toolLabels: Record<string, string> = {
  calculator: "Calculator",
  products: "Product Search",
  outlets: "Outlet Search",
};

export default function ToolCallCard({ toolCall }: ToolCallCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { tool, input, output } = toolCall;

  const isSuccess = output.success;
  const icon = toolIcons[tool] || <Calculator className="h-4 w-4" />;
  const label = toolLabels[tool] || tool;

  return (
    <Card
      className={cn(
        "mb-2 border-l-4",
        isSuccess
          ? "border-l-green-500 bg-green-50 dark:bg-green-950/20"
          : "border-l-red-500 bg-red-50 dark:bg-red-950/20"
      )}
    >
      <CardHeader
        className="pb-2 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {icon}
            <CardTitle className="text-sm font-medium">{label}</CardTitle>
            <span
              className={cn(
                "text-xs px-2 py-0.5 rounded",
                isSuccess
                  ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                  : "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"
              )}
            >
              {isSuccess ? "Success" : "Error"}
            </span>
          </div>
          {isExpanded ? (
            <ChevronUp className="h-4 w-4" />
          ) : (
            <ChevronDown className="h-4 w-4" />
          )}
        </div>
      </CardHeader>
      {isExpanded && (
        <CardContent className="pt-0 space-y-2">
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-1">Input:</p>
            <pre className="text-xs bg-muted p-2 rounded overflow-auto">
              {JSON.stringify(input, null, 2)}
            </pre>
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-1">Output:</p>
            <pre className="text-xs bg-muted p-2 rounded overflow-auto">
              {JSON.stringify(output, null, 2)}
            </pre>
          </div>
        </CardContent>
      )}
    </Card>
  );
}

