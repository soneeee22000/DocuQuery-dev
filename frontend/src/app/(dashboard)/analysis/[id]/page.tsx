"use client";

/**
 * Analysis results dashboard.
 */

import { use } from "react";
import Link from "next/link";

import { AnalysisSkeleton } from "@/components/analysis/analysis-skeleton";
import { CategoryCard } from "@/components/analysis/category-card";
import { ScoreGauge } from "@/components/analysis/score-gauge";
import { TipsList } from "@/components/analysis/tips-list";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useAnalysis } from "@/hooks/use-analysis";

export default function AnalysisResultPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { analysis, isLoading, error, refresh } = useAnalysis(id);

  if (isLoading) return <AnalysisSkeleton />;

  if (error || !analysis) {
    return (
      <div className="mx-auto max-w-4xl space-y-4">
        <nav className="text-sm text-muted-foreground">
          <Link href="/analysis" className="hover:underline">
            Analysis History
          </Link>
          <span className="mx-1">/</span>
          <span>Results</span>
        </nav>
        <div className="flex flex-col items-center gap-4 py-12">
          <p className="text-destructive">{error ?? "Analysis not found"}</p>
          <div className="flex gap-2">
            <Button asChild variant="outline">
              <Link href="/analysis">Back to History</Link>
            </Button>
            <Button onClick={refresh}>Retry</Button>
          </div>
        </div>
      </div>
    );
  }

  const { results, tips } = analysis;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <nav className="text-sm text-muted-foreground">
        <Link href="/analysis" className="hover:underline">
          Analysis History
        </Link>
        <span className="mx-1">/</span>
        <span>Results</span>
      </nav>

      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Analysis Results</h2>
          <p className="text-sm text-muted-foreground">
            {analysis.resume_name} vs {analysis.jd_name}
          </p>
        </div>
      </div>

      <div className="flex justify-center">
        <ScoreGauge score={results.score} />
      </div>

      <Separator />

      <div className="grid gap-4 md:grid-cols-2">
        <CategoryCard
          title="Skills"
          score={results.categories.skills.score}
          matched={results.categories.skills.matched}
          missing={results.categories.skills.missing}
          feedback={results.categories.skills.feedback}
        />
        <CategoryCard
          title="Experience"
          score={results.categories.experience.score}
          matched={results.categories.experience.matched}
          missing={results.categories.experience.missing}
          feedback={results.categories.experience.feedback}
        />
        <CategoryCard
          title="Education"
          score={results.categories.education.score}
          matched={results.categories.education.matched}
          missing={results.categories.education.missing}
          feedback={results.categories.education.feedback}
        />
        <CategoryCard
          title="Keywords"
          score={results.categories.keywords.score}
          matched={results.categories.keywords.matched}
          missing={results.categories.keywords.missing}
          feedback={results.categories.keywords.feedback}
        />
      </div>

      <TipsList tips={tips} />
    </div>
  );
}
