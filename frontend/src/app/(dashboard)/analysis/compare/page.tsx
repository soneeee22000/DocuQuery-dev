"use client";

/**
 * Comparison results page — shows delta between two analyses.
 */

import { Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { AnalysisSkeleton } from "@/components/analysis/analysis-skeleton";
import { CategoryDeltaGrid } from "@/components/analysis/category-delta-grid";
import { ScoreDeltaBanner } from "@/components/analysis/score-delta-banner";
import { Button } from "@/components/ui/button";
import { useComparison } from "@/hooks/use-analysis";

function ComparisonContent() {
  const searchParams = useSearchParams();
  const currentId = searchParams.get("current") ?? "";
  const previousId = searchParams.get("previous") ?? "";

  const { comparison, isLoading, error, refresh } = useComparison(
    currentId,
    previousId,
  );

  if (isLoading) return <AnalysisSkeleton />;

  if (error || !comparison) {
    return (
      <div className="flex flex-col items-center gap-4 py-12">
        <p className="text-destructive">{error ?? "Comparison not found"}</p>
        <div className="flex gap-2">
          <Button asChild variant="outline">
            <Link href="/analysis">Back to History</Link>
          </Button>
          <Button onClick={refresh}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <ScoreDeltaBanner
        delta={comparison.score_delta}
        currentScore={comparison.current.score}
        previousScore={comparison.previous.score}
      />

      <div className="text-sm text-muted-foreground">
        <p>
          <strong>Current:</strong> {comparison.current.resume_name} vs{" "}
          {comparison.current.jd_name}
        </p>
        <p>
          <strong>Previous:</strong> {comparison.previous.resume_name} vs{" "}
          {comparison.previous.jd_name}
        </p>
      </div>

      <CategoryDeltaGrid deltas={comparison.category_deltas} />
    </div>
  );
}

export default function ComparisonPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <nav className="text-sm text-muted-foreground">
        <Link href="/analysis" className="hover:underline">
          Analysis History
        </Link>
        <span className="mx-1">/</span>
        <span>Comparison</span>
      </nav>
      <h2 className="text-2xl font-semibold">Analysis Comparison</h2>
      <Suspense fallback={<AnalysisSkeleton />}>
        <ComparisonContent />
      </Suspense>
    </div>
  );
}
