/** Skills category breakdown. */
export interface CategorySkills {
  score: number;
  matched: string[];
  missing: string[];
  feedback: string;
}

/** Experience category breakdown. */
export interface CategoryExperience {
  score: number;
  matched: string[];
  missing: string[];
  feedback: string;
}

/** Education category breakdown. */
export interface CategoryEducation {
  score: number;
  matched: string[];
  missing: string[];
  feedback: string;
}

/** Keywords category breakdown. */
export interface CategoryKeywords {
  score: number;
  matched: string[];
  missing: string[];
  feedback: string;
}

/** All category breakdowns. */
export interface AnalysisCategories {
  skills: CategorySkills;
  experience: CategoryExperience;
  education: CategoryEducation;
  keywords: CategoryKeywords;
}

/** A single improvement tip. */
export interface AnalysisTip {
  priority: number;
  category: string;
  suggestion: string;
  section: string;
}

/** Full analysis results from LLM. */
export interface AnalysisResults {
  score: number;
  categories: AnalysisCategories;
  keyword_gaps: string[];
}

/** Full analysis response including metadata. */
export interface Analysis {
  id: string;
  resume_id: string;
  jd_id: string;
  resume_name: string;
  jd_name: string;
  score: number;
  results: AnalysisResults;
  tips: AnalysisTip[];
  llm_model: string;
  created_at: string;
}

/** Summary for analysis history list. */
export interface AnalysisSummary {
  id: string;
  resume_name: string;
  jd_name: string;
  score: number;
  llm_model: string;
  created_at: string;
}

/** Score change for a single category. */
export interface CategoryDelta {
  category: string;
  previous: number;
  current: number;
  delta: number;
}

/** Comparison between two analyses. */
export interface AnalysisComparison {
  current: Analysis;
  previous: Analysis;
  score_delta: number;
  category_deltas: CategoryDelta[];
}

/** Request to trigger a match analysis. */
export interface MatchRequest {
  resume_id: string;
  jd_id: string;
}
