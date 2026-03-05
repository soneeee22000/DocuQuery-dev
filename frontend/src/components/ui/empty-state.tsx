/**
 * Shared empty state component with optional CTA action.
 */

import { Card, CardContent } from "@/components/ui/card";

interface EmptyStateProps {
  /** Message to display. */
  message: string;
  /** Optional action slot (e.g., a button). */
  action?: React.ReactNode;
}

export function EmptyState({ message, action }: EmptyStateProps) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center gap-4 py-12 text-center">
        <p className="text-muted-foreground">{message}</p>
        {action}
      </CardContent>
    </Card>
  );
}
