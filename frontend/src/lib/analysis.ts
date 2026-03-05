/**
 * Analysis API functions.
 */

import type { ApiResponse } from "@/types/api";
import type {
  Analysis,
  AnalysisComparison,
  AnalysisSummary,
  MatchRequest,
} from "@/types/analysis";

import apiClient from "./api-client";

/** Trigger a new match analysis. */
export async function triggerAnalysis(body: MatchRequest): Promise<Analysis> {
  const { data } = await apiClient.post<ApiResponse<Analysis>>(
    "/analysis/match",
    body,
  );
  return data.data!;
}

/** Get a single analysis by ID. */
export async function getAnalysis(id: string): Promise<Analysis> {
  const { data } = await apiClient.get<ApiResponse<Analysis>>(
    `/analysis/${id}`,
  );
  return data.data!;
}

/** List all analyses for the current user. */
export async function listAnalyses(): Promise<AnalysisSummary[]> {
  const { data } =
    await apiClient.get<ApiResponse<AnalysisSummary[]>>("/analysis/");
  return data.data!;
}

/** Compare two analyses. */
export async function compareAnalyses(
  currentId: string,
  previousId: string,
): Promise<AnalysisComparison> {
  const { data } = await apiClient.get<ApiResponse<AnalysisComparison>>(
    `/analysis/${currentId}/compare/${previousId}`,
  );
  return data.data!;
}
