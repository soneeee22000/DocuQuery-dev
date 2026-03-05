"""Tips prioritization and serialization."""

from typing import Any

from app.schemas.analysis import AnalysisTip


def prioritize_tips(tips: list[AnalysisTip]) -> list[AnalysisTip]:
    """Sort tips by priority (ascending: 1 = highest priority)."""
    return sorted(tips, key=lambda t: t.priority)


def tips_to_dicts(tips: list[AnalysisTip]) -> list[dict[str, Any]]:
    """Serialize tips to list of dicts for JSON storage."""
    return [tip.model_dump() for tip in tips]
