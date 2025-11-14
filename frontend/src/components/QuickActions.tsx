import { Button } from "./ui/button";
import { Calculator, ShoppingBag, MapPin, RotateCcw } from "lucide-react";

const actions = [
  { label: "Calculator", action: "What can you calculate?", icon: Calculator },
  { label: "Products", action: "Show me products", icon: ShoppingBag },
  { label: "Outlets", action: "Find outlets near me", icon: MapPin },
  { label: "Reset", action: "reset", icon: RotateCcw },
];

interface QuickActionsProps {
  onAction: (action: string) => void;
  disabled?: boolean;
}

export default function QuickActions({ onAction, disabled = false }: QuickActionsProps) {
  return (
    <div className="py-3">
      <div className="flex flex-wrap gap-2">
        {actions.map((item) => {
          const Icon = item.icon;
          return (
            <Button
              key={item.label}
              onClick={() => onAction(item.action)}
              disabled={disabled}
              variant="outline"
              size="sm"
              className="gap-2 border-border/60 hover:bg-accent/50 hover:border-primary/30 transition-all"
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </Button>
          );
        })}
      </div>
    </div>
  );
}
