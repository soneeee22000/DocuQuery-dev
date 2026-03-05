"use client";

/**
 * 2x2 grid showing category score deltas between two analyses.
 */

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { CategoryDelta } from "@/types/analysis";

interface CategoryDeltaGridProps {
  /** Array of category deltas. */
  deltas: CategoryDelta[];
}

export function CategoryDeltaGrid({ deltas }: CategoryDeltaGridProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {deltas.map((d) => (
        <Card key={d.category}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium capitalize">
              {d.category}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">
                {d.previous} &rarr; {d.current}
              </span>
              <span
                className={`text-sm font-bold ${
                  d.delta > 0
                    ? "text-green-500"
                    : d.delta < 0
                      ? "text-red-500"
                      : "text-muted-foreground"
                }`}
              >
                {d.delta > 0 ? "+" : ""}
                {d.delta}
              </span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
