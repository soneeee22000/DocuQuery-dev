"""Tests for analyzer service."""

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.common import AppError
from app.services.analyzer import run_analysis


def _make_completion(content: dict[str, Any]) -> MagicMock:
    """Build a mock chat completion response."""
    choice = MagicMock()
    choice.message.content = json.dumps(content)
    response = MagicMock()
    response.choices = [choice]
    return response


VALID_LLM_RESPONSE: dict[str, Any] = {
    "score": 75,
    "categories": {
        "skills": {
            "score": 80,
            "matched": ["Python", "FastAPI"],
            "missing": ["Go"],
            "feedback": "Strong Python skills.",
        },
        "experience": {
            "score": 70,
            "matched": ["3 years backend"],
            "missing": ["team lead"],
            "feedback": "Solid experience.",
        },
        "education": {
            "score": 65,
            "matched": ["BS Computer Science"],
            "missing": [],
            "feedback": "Meets requirements.",
        },
        "keywords": {
            "score": 85,
            "matched": ["API", "REST", "microservices"],
            "missing": ["Kubernetes"],
            "feedback": "Good keyword coverage.",
        },
    },
    "keyword_gaps": ["Go", "Kubernetes"],
    "tips": [
        {
            "priority": 1,
            "category": "skills",
            "suggestion": "Add Go experience",
            "section": "Skills",
        },
        {
            "priority": 2,
            "category": "keywords",
            "suggestion": "Mention Kubernetes",
            "section": "Experience",
        },
        {
            "priority": 3,
            "category": "experience",
            "suggestion": "Highlight leadership",
            "section": "Experience",
        },
        {
            "priority": 4,
            "category": "education",
            "suggestion": "Add certifications",
            "section": "Education",
        },
        {
            "priority": 5,
            "category": "skills",
            "suggestion": "Add CI/CD tools",
            "section": "Skills",
        },
    ],
}


@patch("app.services.analyzer.AsyncOpenAI")
async def test_run_analysis_success(mock_openai_cls: MagicMock) -> None:
    """Successful analysis returns parsed results and tips."""
    mock_client = AsyncMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _make_completion(
        VALID_LLM_RESPONSE
    )

    results, tips = await run_analysis("Resume text here", "Job description here")

    assert results.score == 75
    assert results.categories.skills.score == 80
    assert "Python" in results.categories.skills.matched
    assert len(tips) == 5
    assert tips[0].priority == 1


@patch("app.services.analyzer.AsyncOpenAI")
async def test_run_analysis_timeout_then_raise(mock_openai_cls: MagicMock) -> None:
    """Two consecutive timeouts raise AppError with 504."""
    from openai import APITimeoutError

    mock_client = AsyncMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.side_effect = APITimeoutError(
        request=MagicMock()
    )

    with pytest.raises(AppError) as exc_info:
        await run_analysis("Resume", "JD")

    assert exc_info.value.status_code == 504
    assert exc_info.value.code == "LLM_TIMEOUT"


@patch("app.services.analyzer.AsyncOpenAI")
async def test_run_analysis_timeout_then_succeed(mock_openai_cls: MagicMock) -> None:
    """First call times out, retry succeeds."""
    from openai import APITimeoutError

    mock_client = AsyncMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.side_effect = [
        APITimeoutError(request=MagicMock()),
        _make_completion(VALID_LLM_RESPONSE),
    ]

    results, tips = await run_analysis("Resume", "JD")
    assert results.score == 75
    assert len(tips) == 5


@patch("app.services.analyzer.AsyncOpenAI")
async def test_run_analysis_rate_limit(mock_openai_cls: MagicMock) -> None:
    """Rate limit raises AppError with 429."""
    from openai import RateLimitError

    mock_client = AsyncMock()
    mock_openai_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {}
    mock_client.chat.completions.create.side_effect = RateLimitError(
        message="Rate limited",
        response=mock_response,
        body=None,
    )

    with pytest.raises(AppError) as exc_info:
        await run_analysis("Resume", "JD")

    assert exc_info.value.status_code == 429
    assert exc_info.value.code == "RATE_LIMIT"


@patch("app.services.analyzer.AsyncOpenAI")
async def test_run_analysis_malformed_json(mock_openai_cls: MagicMock) -> None:
    """Malformed JSON from LLM raises AppError with 502."""
    mock_client = AsyncMock()
    mock_openai_cls.return_value = mock_client

    choice = MagicMock()
    choice.message.content = "not valid json {{"
    response = MagicMock()
    response.choices = [choice]
    mock_client.chat.completions.create.return_value = response

    with pytest.raises(Exception):
        await run_analysis("Resume", "JD")


@patch("app.services.analyzer.AsyncOpenAI")
async def test_run_analysis_schema_mismatch(mock_openai_cls: MagicMock) -> None:
    """Valid JSON but wrong schema raises AppError with 502."""
    mock_client = AsyncMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _make_completion(
        {"score": 50}  # missing categories
    )

    with pytest.raises(AppError) as exc_info:
        await run_analysis("Resume", "JD")

    assert exc_info.value.status_code == 502
    assert exc_info.value.code == "LLM_PARSE_ERROR"


@patch("app.services.analyzer.AsyncOpenAI")
async def test_run_analysis_short_text(mock_openai_cls: MagicMock) -> None:
    """Short resume/JD text still processes successfully."""
    mock_client = AsyncMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _make_completion(
        VALID_LLM_RESPONSE
    )

    results, tips = await run_analysis("Short", "Also short")
    assert results.score == 75
    mock_client.chat.completions.create.assert_called_once()
