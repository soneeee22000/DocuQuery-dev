"use client";

/**
 * Banner showing overall score delta between two analyses.
 */

import { ArrowUp, ArrowDown, Minus } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";

interface ScoreDeltaBannerProps {
  /** Score difference (current - previous). */
  delta: number;
  /** Current analysis score. */
  currentScore: number;
  /** Previous analysis score. */
  previousScore: number;
}

export function ScoreDeltaBanner({
  delta,
  currentScore,
  previousScore,
}: ScoreDeltaBannerProps) {
  const isPositive = delta > 0;
  const isNegative = delta < 0;

  return (
    <Card>
      <CardContent className="flex flex-col items-center gap-2 py-8">
        <div className="flex items-center gap-2">
          {isPositive && <ArrowUp className="h-8 w-8 text-green-500" />}
          {isNegative && <ArrowDown className="h-8 w-8 text-red-500" />}
          {!isPositive && !isNegative && (
            <Minus className="h-8 w-8 text-muted-foreground" />
          )}
          <span
            className={`text-4xl font-bold ${
              isPositive
                ? "text-green-500"
                : isNegative
                  ? "text-red-500"
                  : "text-muted-foreground"
            }`}
          >
            {isPositive ? "+" : ""}
            {delta}
          </span>
        </div>
        <p className="text-sm text-muted-foreground">
          {previousScore} &rarr; {currentScore} overall score
        </p>
      </CardContent>
    </Card>
  );
}
