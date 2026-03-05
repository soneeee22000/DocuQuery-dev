"use client";

/**
 * Numbered list of improvement tips with category badges.
 */

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AnalysisTip } from "@/types/analysis";

interface TipsListProps {
  /** List of prioritized tips. */
  tips: AnalysisTip[];
}

const CATEGORY_COLORS: Record<string, string> = {
  skills: "bg-blue-600",
  experience: "bg-purple-600",
  education: "bg-orange-600",
  keywords: "bg-teal-600",
};

export function TipsList({ tips }: TipsListProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Improvement Tips</CardTitle>
      </CardHeader>
      <CardContent>
        <ol className="space-y-4">
          {tips.map((tip, index) => (
            <li key={index} className="flex gap-3">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
                {index + 1}
              </span>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Badge
                    className={CATEGORY_COLORS[tip.category] ?? "bg-secondary"}
                  >
                    {tip.category}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {tip.section}
                  </span>
                </div>
                <p className="text-sm">{tip.suggestion}</p>
              </div>
            </li>
          ))}
        </ol>
      </CardContent>
    </Card>
  );
}
