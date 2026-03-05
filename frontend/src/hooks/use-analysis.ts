"use client";

/**
 * Hooks for analysis operations.
 */

import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

import {
  compareAnalyses,
  getAnalysis,
  listAnalyses,
  triggerAnalysis,
} from "@/lib/analysis";
import type {
  Analysis,
  AnalysisComparison,
  AnalysisSummary,
  MatchRequest,
} from "@/types/analysis";

/** Hook for fetching analysis history. */
export function useAnalysisHistory() {
  const [analyses, setAnalyses] = useState<AnalysisSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setAnalyses(await listAnalyses());
    } catch {
      const msg = "Failed to load analyses";
      setError(msg);
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { analyses, isLoading, error, refresh: fetch };
}

/** Hook for triggering a new analysis. */
export function useAnalysisTrigger() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const trigger = useCallback(async (body: MatchRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      return await triggerAnalysis(body);
    } catch {
      const msg = "Analysis failed. Please try again.";
      setError(msg);
      toast.error(msg);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { trigger, isLoading, error };
}

/** Hook for fetching a single analysis with retry support. */
export function useAnalysis(id: string) {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  const fetchAnalysis = useCallback(async () => {
    try {
      const data = await getAnalysis(id);
      setAnalysis(data);
      setError(null);
    } catch {
      setError("Failed to load analysis");
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    setAnalysis(null);
    fetchAnalysis();
  }, [fetchAnalysis, retryCount]);

  const refresh = useCallback(() => {
    setRetryCount((c) => c + 1);
  }, []);

  return { analysis, isLoading, error, refresh };
}

/** Hook for comparing two analyses. */
export function useComparison(currentId: string, previousId: string) {
  const hasIds = Boolean(currentId && previousId);
  const [comparison, setComparison] = useState<AnalysisComparison | null>(null);
  const [isLoading, setIsLoading] = useState(hasIds);
  const [error, setError] = useState<string | null>(
    hasIds ? null : "Two analysis IDs are required for comparison",
  );
  const [retryCount, setRetryCount] = useState(0);

  const fetchComparison = useCallback(async () => {
    if (!currentId || !previousId) return;
    try {
      const data = await compareAnalyses(currentId, previousId);
      setComparison(data);
      setError(null);
    } catch {
      setError("Failed to load comparison");
    } finally {
      setIsLoading(false);
    }
  }, [currentId, previousId]);

  useEffect(() => {
    if (!currentId || !previousId) return;
    fetchComparison();
  }, [currentId, previousId, fetchComparison, retryCount]);

  const refresh = useCallback(() => {
    setRetryCount((c) => c + 1);
  }, []);

  return { comparison, isLoading, error, refresh };
}
