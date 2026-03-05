"use client";

/**
 * Category breakdown card with progress bar and badges.
 */

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

interface CategoryCardProps {
  /** Category display name. */
  title: string;
  /** Score 0-100. */
  score: number;
  /** Matched items. */
  matched: string[];
  /** Missing items. */
  missing: string[];
  /** LLM feedback text. */
  feedback: string;
}

export function CategoryCard({
  title,
  score,
  matched,
  missing,
  feedback,
}: CategoryCardProps) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">{title}</CardTitle>
          <span className="text-sm font-semibold">{score}/100</span>
        </div>
        <Progress value={score} className="h-2" />
      </CardHeader>
      <CardContent className="space-y-3">
        {matched.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {matched.map((item) => (
              <Badge key={item} variant="default" className="bg-green-600">
                {item}
              </Badge>
            ))}
          </div>
        )}
        {missing.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {missing.map((item) => (
              <Badge key={item} variant="destructive">
                {item}
              </Badge>
            ))}
          </div>
        )}
        <p className="text-sm text-muted-foreground">{feedback}</p>
      </CardContent>
    </Card>
  );
}
