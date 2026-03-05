"""Analysis schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    """Request to trigger a match analysis."""

    resume_id: uuid.UUID
    jd_id: uuid.UUID


class CategorySkills(BaseModel):
    """Skills category breakdown."""

    score: int = Field(ge=0, le=100)
    matched: list[str]
    missing: list[str]
    feedback: str


class CategoryExperience(BaseModel):
    """Experience category breakdown."""

    score: int = Field(ge=0, le=100)
    matched: list[str]
    missing: list[str]
    feedback: str


class CategoryEducation(BaseModel):
    """Education category breakdown."""

    score: int = Field(ge=0, le=100)
    matched: list[str]
    missing: list[str]
    feedback: str


class CategoryKeywords(BaseModel):
    """Keywords category breakdown."""

    score: int = Field(ge=0, le=100)
    matched: list[str]
    missing: list[str]
    feedback: str


class AnalysisCategories(BaseModel):
    """All category breakdowns."""

    skills: CategorySkills
    experience: CategoryExperience
    education: CategoryEducation
    keywords: CategoryKeywords


class AnalysisTip(BaseModel):
    """A single improvement tip."""

    priority: int = Field(ge=1, le=5)
    category: str
    suggestion: str
    section: str


class AnalysisResults(BaseModel):
    """Full analysis results from LLM."""

    score: int = Field(ge=0, le=100)
    categories: AnalysisCategories
    keyword_gaps: list[str]


class AnalysisResponse(BaseModel):
    """Full analysis response including metadata."""

    id: uuid.UUID
    resume_id: uuid.UUID
    jd_id: uuid.UUID
    resume_name: str
    jd_name: str
    score: int
    results: AnalysisResults
    tips: list[AnalysisTip]
    llm_model: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisSummary(BaseModel):
    """Summary for analysis history list."""

    id: uuid.UUID
    resume_name: str
    jd_name: str
    score: int
    llm_model: str
    created_at: datetime


class CategoryDelta(BaseModel):
    """Score change for a single category."""

    category: str
    previous: int
    current: int
    delta: int


class CompareResponse(BaseModel):
    """Comparison between two analyses."""

    current: AnalysisResponse
    previous: AnalysisResponse
    score_delta: int
    category_deltas: list[CategoryDelta]
