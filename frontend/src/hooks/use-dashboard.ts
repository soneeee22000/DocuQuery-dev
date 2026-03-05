"use client";

/**
 * Hook for dashboard statistics.
 */

import { useCallback, useEffect, useState } from "react";

import { listDocuments } from "@/lib/documents";
import { listAnalyses } from "@/lib/analysis";
import type { AnalysisSummary } from "@/types/analysis";

export interface DashboardStats {
  resumeCount: number;
  jdCount: number;
  analysisCount: number;
  averageScore: number;
  recentAnalyses: AnalysisSummary[];
}

export function useDashboardStats() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [docs, analyses] = await Promise.all([
        listDocuments(),
        listAnalyses(),
      ]);

      const resumeCount = docs.filter((d) => d.doc_type === "resume").length;
      const jdCount = docs.filter(
        (d) => d.doc_type === "job_description",
      ).length;
      const analysisCount = analyses.length;
      const averageScore =
        analysisCount > 0
          ? Math.round(
              analyses.reduce((sum, a) => sum + a.score, 0) / analysisCount,
            )
          : 0;
      const recentAnalyses = analyses.slice(0, 3);

      setStats({
        resumeCount,
        jdCount,
        analysisCount,
        averageScore,
        recentAnalyses,
      });
    } catch {
      setError("Failed to load dashboard data");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { stats, isLoading, error, refresh: fetch };
}
