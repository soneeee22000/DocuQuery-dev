"""Tests for analysis schema validation."""

import uuid

import pytest
from pydantic import ValidationError

from app.schemas.analysis import (
    AnalysisResults,
    AnalysisTip,
    CategoryEducation,
    CategoryExperience,
    CategoryKeywords,
    CategorySkills,
    MatchRequest,
)


def test_match_request_valid() -> None:
    """MatchRequest accepts valid UUIDs."""
    req = MatchRequest(resume_id=uuid.uuid4(), jd_id=uuid.uuid4())
    assert req.resume_id is not None
    assert req.jd_id is not None


def test_match_request_invalid_uuid() -> None:
    """MatchRequest rejects non-UUID values."""
    with pytest.raises(ValidationError):
        MatchRequest(resume_id="not-a-uuid", jd_id="also-bad")  # type: ignore[arg-type]


def test_analysis_results_score_bounds() -> None:
    """AnalysisResults rejects scores outside 0-100."""
    categories = {
        "skills": CategorySkills(
            score=80, matched=["Python"], missing=["Go"], feedback="Good"
        ),
        "experience": CategoryExperience(
            score=70, matched=["3 years"], missing=[], feedback="Solid"
        ),
        "education": CategoryEducation(
            score=60, matched=["BS CS"], missing=[], feedback="OK"
        ),
        "keywords": CategoryKeywords(
            score=90, matched=["API"], missing=["K8s"], feedback="Strong"
        ),
    }
    with pytest.raises(ValidationError):
        AnalysisResults(score=101, categories=categories, keyword_gaps=["K8s"])

    with pytest.raises(ValidationError):
        AnalysisResults(score=-1, categories=categories, keyword_gaps=[])


def test_analysis_tip_priority_bounds() -> None:
    """AnalysisTip rejects priorities outside 1-5."""
    with pytest.raises(ValidationError):
        AnalysisTip(priority=0, category="skills", suggestion="Add X", section="Skills")

    with pytest.raises(ValidationError):
        AnalysisTip(priority=6, category="skills", suggestion="Add X", section="Skills")

    tip = AnalysisTip(
        priority=1, category="skills", suggestion="Add Python", section="Skills"
    )
    assert tip.priority == 1
