"""LLM-powered resume-job match analyzer."""

import json
import logging
from typing import Any

from openai import APITimeoutError, AsyncOpenAI, RateLimitError

from app.core.config import settings
from app.schemas.analysis import AnalysisResults, AnalysisTip

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a resume-job match analyst. \
Analyze how well the resume matches the job description.

Return a JSON object with this exact structure:
{
  "score": <0-100 overall match score>,
  "categories": {
    "skills": {
      "score": <0-100>,
      "matched": ["skill1", "skill2"],
      "missing": ["skill3"],
      "feedback": "Brief feedback on skills match"
    },
    "experience": {
      "score": <0-100>,
      "matched": ["experience1"],
      "missing": ["experience2"],
      "feedback": "Brief feedback on experience match"
    },
    "education": {
      "score": <0-100>,
      "matched": ["education1"],
      "missing": [],
      "feedback": "Brief feedback on education match"
    },
    "keywords": {
      "score": <0-100>,
      "matched": ["keyword1"],
      "missing": ["keyword2"],
      "feedback": "Brief feedback on keyword match"
    }
  },
  "keyword_gaps": ["keyword1", "keyword2"],
  "tips": [
    {
      "priority": 1,
      "category": "skills|experience|education|keywords",
      "suggestion": "Specific improvement suggestion",
      "section": "Which resume section to update"
    }
  ]
}

Scoring weights: skills 35%, experience 30%, education 15%, keywords 20%.
The overall score must reflect these weights.
Return exactly 5 tips, ordered by priority (1 = most important).
Only return valid JSON, no markdown or extra text."""

MAX_RESUME_CHARS = 8000
MAX_JD_CHARS = 4000


async def run_analysis(
    resume_text: str,
    jd_text: str,
) -> tuple[AnalysisResults, list[AnalysisTip]]:
    """Run LLM analysis on resume vs job description.

    Args:
        resume_text: Extracted text from resume document.
        jd_text: Extracted text from job description document.

    Returns:
        Tuple of (AnalysisResults, list of AnalysisTip).

    Raises:
        AppError: On LLM timeout or rate limit.
    """
    from app.schemas.common import AppError

    truncated_resume = resume_text[:MAX_RESUME_CHARS]
    truncated_jd = jd_text[:MAX_JD_CHARS]

    user_prompt = f"## Resume\n{truncated_resume}\n\n## Job Description\n{truncated_jd}"

    client = AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        timeout=float(settings.LLM_TIMEOUT_SECONDS),
    )

    raw: dict[str, Any] = {}
    retries = 0
    max_retries = 1

    while retries <= max_retries:
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            content = response.choices[0].message.content or "{}"
            raw = json.loads(content)
            break
        except APITimeoutError as exc:
            if retries < max_retries:
                retries += 1
                logger.warning(
                    "OpenAI timeout, retrying (%d/%d)",
                    retries,
                    max_retries,
                )
                continue
            raise AppError(
                code="LLM_TIMEOUT",
                message="Analysis timed out. Please try again.",
                status_code=504,
            ) from exc
        except RateLimitError as exc:
            raise AppError(
                code="RATE_LIMIT",
                message="Rate limit exceeded. Please wait and try again.",
                status_code=429,
            ) from exc

    try:
        results = AnalysisResults(
            score=raw["score"],
            categories=raw["categories"],
            keyword_gaps=raw.get("keyword_gaps", []),
        )
    except (KeyError, TypeError) as exc:
        logger.error("Failed to parse LLM response: %s", exc)
        raise AppError(
            code="LLM_PARSE_ERROR",
            message="Failed to parse analysis results. Please try again.",
            status_code=502,
        ) from exc

    raw_tips = raw.get("tips", [])
    try:
        tips = [AnalysisTip(**tip) for tip in raw_tips[:5]]
    except (TypeError, KeyError) as exc:
        logger.error("Failed to parse tips: %s", exc)
        tips = []

    return results, tips
