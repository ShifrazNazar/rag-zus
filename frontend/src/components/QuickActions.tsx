/**
 * QuickActions component for quick action buttons.
 */
import { Button } from "./ui/button";
import { Calculator, ShoppingBag, MapPin, RotateCcw } from "lucide-react";

interface QuickAction {
  label: string;
  action: string;
  description?: string;
  icon: React.ReactNode;
}

const quickActions: QuickAction[] = [
  {
    label: "Calculator",
    action: "/calc",
    description: "Perform calculations",
    icon: <Calculator className="h-4 w-4" />,
  },
  {
    label: "Products",
    action: "/products",
    description: "Search products",
    icon: <ShoppingBag className="h-4 w-4" />,
  },
  {
    label: "Outlets",
    action: "/outlets",
    description: "Find outlets",
    icon: <MapPin className="h-4 w-4" />,
  },
  {
    label: "Reset",
    action: "/reset",
    description: "Clear conversation",
    icon: <RotateCcw className="h-4 w-4" />,
  },
];

interface QuickActionsProps {
  onAction: (action: string) => void;
  disabled?: boolean;
}

export default function QuickActions({
  onAction,
  disabled = false,
}: QuickActionsProps) {
  const handleAction = (action: string) => {
    if (disabled) return;

    switch (action) {
      case "/calc":
        onAction("What can you calculate?");
        break;
      case "/products":
        onAction("Show me products");
        break;
      case "/outlets":
        onAction("Find outlets near me");
        break;
      case "/reset":
        onAction("reset");
        break;
      default:
        onAction(action);
    }
  };

  return (
    <div className="border-b border-border bg-muted/50 px-4 py-3">
      <div className="flex flex-wrap gap-2">
        {quickActions.map((action) => (
          <Button
            key={action.action}
            onClick={() => handleAction(action.action)}
            disabled={disabled}
            variant="outline"
            size="sm"
            className="gap-2"
            title={action.description}
          >
            {action.icon}
            {action.label}
          </Button>
        ))}
      </div>
    </div>
  );
}
