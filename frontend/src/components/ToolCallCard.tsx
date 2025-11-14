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
        "mb-2 border-l-4 shadow-sm",
        isSuccess
          ? "border-l-primary bg-primary/5 dark:bg-primary/10"
          : "border-l-destructive bg-destructive/5 dark:bg-destructive/10"
      )}
    >
      <CardHeader
        className="pb-2 cursor-pointer hover:bg-accent/30 transition-colors rounded-t-lg"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {icon}
            <CardTitle className="text-sm font-medium">{label}</CardTitle>
            <span
              className={cn(
                "text-xs px-2 py-0.5 rounded-md font-medium",
                isSuccess
                  ? "bg-primary/20 text-primary dark:bg-primary/30 dark:text-primary-foreground"
                  : "bg-destructive/20 text-destructive dark:bg-destructive/30 dark:text-destructive-foreground"
              )}
            >
              {isSuccess ? "Success" : "Error"}
            </span>
          </div>
          {isExpanded ? (
            <ChevronUp className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          )}
        </div>
      </CardHeader>
      {isExpanded && (
        <CardContent className="pt-0 space-y-3">
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-1.5">Input:</p>
            <pre className="text-xs bg-muted/50 border border-border/60 p-2.5 rounded-lg overflow-auto font-mono">
              {JSON.stringify(input, null, 2)}
            </pre>
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-1.5">Output:</p>
            <pre className="text-xs bg-muted/50 border border-border/60 p-2.5 rounded-lg overflow-auto font-mono">
              {JSON.stringify(output, null, 2)}
            </pre>
          </div>
        </CardContent>
      )}
    </Card>
  );
}

