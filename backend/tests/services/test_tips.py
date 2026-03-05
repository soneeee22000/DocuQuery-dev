"""Tests for tips service."""

from app.schemas.analysis import AnalysisTip
from app.services.tips import prioritize_tips, tips_to_dicts


def test_prioritize_tips_sort_order() -> None:
    """Tips are sorted by priority ascending."""
    tips = [
        AnalysisTip(priority=3, category="skills", suggestion="C", section="Skills"),
        AnalysisTip(priority=1, category="experience", suggestion="A", section="Exp"),
        AnalysisTip(priority=2, category="keywords", suggestion="B", section="KW"),
    ]

    sorted_tips = prioritize_tips(tips)

    assert [t.priority for t in sorted_tips] == [1, 2, 3]
    assert sorted_tips[0].suggestion == "A"


def test_tips_to_dicts_serialization() -> None:
    """Tips serialize to list of dicts."""
    tips = [
        AnalysisTip(
            priority=1, category="skills", suggestion="Add Python", section="Skills"
        ),
    ]

    result = tips_to_dicts(tips)

    assert len(result) == 1
    assert result[0]["priority"] == 1
    assert result[0]["category"] == "skills"
    assert result[0]["suggestion"] == "Add Python"
    assert result[0]["section"] == "Skills"
