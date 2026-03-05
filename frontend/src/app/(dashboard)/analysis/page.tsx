"use client";

/**
 * Analysis history page with comparison checkbox selection.
 */

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { useAnalysisHistory } from "@/hooks/use-analysis";
import { formatDate, getScoreVariant } from "@/lib/score-utils";

export default function AnalysisHistoryPage() {
  const { analyses, isLoading, error, refresh } = useAnalysisHistory();
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const router = useRouter();

  const toggleSelect = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else if (next.size < 2) {
        next.add(id);
      }
      return next;
    });
  };

  const handleCompare = () => {
    const ids = Array.from(selected);
    if (ids.length !== 2) return;

    const a = analyses.find((x) => x.id === ids[0]);
    const b = analyses.find((x) => x.id === ids[1]);
    if (!a || !b) return;

    const [current, previous] =
      new Date(a.created_at) > new Date(b.created_at) ? [a, b] : [b, a];
    router.push(
      `/analysis/compare?current=${current.id}&previous=${previous.id}`,
    );
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Analysis History</h2>
        <div className="flex gap-2">
          {selected.size === 2 && (
            <Button variant="outline" onClick={handleCompare}>
              Compare Selected
            </Button>
          )}
          <Button asChild>
            <Link href="/analysis/new">New Analysis</Link>
          </Button>
        </div>
      </div>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </div>
      )}

      {error && !isLoading && (
        <div className="flex flex-col items-center gap-4 py-8">
          <p className="text-destructive">{error}</p>
          <Button onClick={refresh}>Retry</Button>
        </div>
      )}

      {!isLoading && !error && analyses.length === 0 && (
        <EmptyState
          message="No analyses yet. Start by creating a new analysis."
          action={
            <Button asChild>
              <Link href="/analysis/new">New Analysis</Link>
            </Button>
          }
        />
      )}

      {analyses.map((a) => (
        <Card key={a.id}>
          <CardContent className="flex items-center justify-between py-4">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={selected.has(a.id)}
                onChange={() => toggleSelect(a.id)}
                disabled={!selected.has(a.id) && selected.size >= 2}
                className="h-4 w-4 rounded border-input accent-primary"
                aria-label={`Select ${a.resume_name} vs ${a.jd_name}`}
              />
              <div className="space-y-1">
                <p className="text-sm font-medium">
                  {a.resume_name} &rarr; {a.jd_name}
                </p>
                <p className="text-xs text-muted-foreground">
                  {formatDate(a.created_at)}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant={getScoreVariant(a.score)}>{a.score}/100</Badge>
              <Button asChild variant="outline" size="sm">
                <Link href={`/analysis/${a.id}`}>View Results</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
