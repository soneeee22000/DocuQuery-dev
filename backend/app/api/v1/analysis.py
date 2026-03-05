"""Analysis endpoints for resume-job match."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.analysis import Analysis
from app.models.document import Document
from app.models.user import User
from app.schemas.analysis import (
    AnalysisResponse,
    AnalysisResults,
    AnalysisSummary,
    AnalysisTip,
    CategoryDelta,
    CompareResponse,
    MatchRequest,
)
from app.schemas.common import ApiResponse, AppError
from app.services.analyzer import run_analysis
from app.services.tips import prioritize_tips, tips_to_dicts

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _build_response(analysis: Analysis) -> AnalysisResponse:
    """Build an AnalysisResponse from an Analysis model instance."""
    return AnalysisResponse(
        id=analysis.id,
        resume_id=analysis.resume_id,
        jd_id=analysis.jd_id,
        resume_name=analysis.resume.name,
        jd_name=analysis.jd.name,
        score=analysis.score,
        results=AnalysisResults.model_validate(analysis.results),
        tips=[AnalysisTip.model_validate(t) for t in (analysis.tips or [])],
        llm_model=analysis.llm_model,
        created_at=analysis.created_at,
    )


async def _get_owned_document(
    db: AsyncSession,
    doc_id: uuid.UUID,
    user_id: uuid.UUID,
    expected_type: str,
) -> Document:
    """Fetch a document owned by the user with the expected type.

    Raises:
        AppError: 404 if not found or not owned, 400 if wrong type.
    """
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()

    if doc is None or doc.user_id != user_id:
        raise AppError(
            code="NOT_FOUND",
            message=f"Document {doc_id} not found",
            status_code=404,
        )

    if doc.doc_type != expected_type:
        raise AppError(
            code="WRONG_DOC_TYPE",
            message=f"Expected {expected_type}, got {doc.doc_type}",
            status_code=400,
        )

    if not doc.extracted_text:
        raise AppError(
            code="NO_TEXT",
            message="Document has no extracted text",
            status_code=400,
        )

    return doc


@router.post("/match", response_model=ApiResponse[AnalysisResponse], status_code=201)
async def trigger_analysis(
    body: MatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[AnalysisResponse]:
    """Trigger a new match analysis between a resume and job description."""
    resume = await _get_owned_document(
        db, body.resume_id, current_user.id, "resume"
    )
    jd = await _get_owned_document(
        db, body.jd_id, current_user.id, "job_description"
    )

    assert resume.extracted_text is not None
    assert jd.extracted_text is not None

    results, tips = await run_analysis(resume.extracted_text, jd.extracted_text)
    sorted_tips = prioritize_tips(tips)

    analysis = Analysis(
        user_id=current_user.id,
        resume_id=resume.id,
        jd_id=jd.id,
        score=results.score,
        results=results.model_dump(),
        tips=tips_to_dicts(sorted_tips),
        llm_model=settings.OPENAI_MODEL,
    )
    db.add(analysis)
    await db.flush()
    await db.refresh(analysis)

    return ApiResponse(data=_build_response(analysis))


@router.get("/{analysis_id}", response_model=ApiResponse[AnalysisResponse])
async def get_analysis(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[AnalysisResponse]:
    """Get a single analysis result."""
    result = await db.execute(
        select(Analysis)
        .options(joinedload(Analysis.resume), joinedload(Analysis.jd))
        .where(Analysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()

    if analysis is None or analysis.user_id != current_user.id:
        raise AppError(
            code="NOT_FOUND",
            message="Analysis not found",
            status_code=404,
        )

    return ApiResponse(data=_build_response(analysis))


@router.get("/", response_model=ApiResponse[list[AnalysisSummary]])
async def list_analyses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[list[AnalysisSummary]]:
    """List all analyses for the current user, newest first."""
    result = await db.execute(
        select(Analysis)
        .options(joinedload(Analysis.resume), joinedload(Analysis.jd))
        .where(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
    )
    analyses = result.unique().scalars().all()

    summaries = [
        AnalysisSummary(
            id=a.id,
            resume_name=a.resume.name,
            jd_name=a.jd.name,
            score=a.score,
            llm_model=a.llm_model,
            created_at=a.created_at,
        )
        for a in analyses
    ]

    return ApiResponse(data=summaries)


@router.get(
    "/{analysis_id}/compare/{prev_id}",
    response_model=ApiResponse[CompareResponse],
)
async def compare_analyses(
    analysis_id: uuid.UUID,
    prev_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[CompareResponse]:
    """Compare two analyses and show score deltas."""
    result = await db.execute(
        select(Analysis)
        .options(joinedload(Analysis.resume), joinedload(Analysis.jd))
        .where(Analysis.id == analysis_id)
    )
    current = result.scalar_one_or_none()

    if current is None or current.user_id != current_user.id:
        raise AppError(
            code="NOT_FOUND",
            message="Current analysis not found",
            status_code=404,
        )

    result2 = await db.execute(
        select(Analysis)
        .options(joinedload(Analysis.resume), joinedload(Analysis.jd))
        .where(Analysis.id == prev_id)
    )
    previous = result2.scalar_one_or_none()

    if previous is None or previous.user_id != current_user.id:
        raise AppError(
            code="NOT_FOUND",
            message="Previous analysis not found",
            status_code=404,
        )

    current_resp = _build_response(current)
    previous_resp = _build_response(previous)

    category_names = ["skills", "experience", "education", "keywords"]
    category_deltas = []
    for cat in category_names:
        cur_score = getattr(current_resp.results.categories, cat).score
        prev_score = getattr(previous_resp.results.categories, cat).score
        category_deltas.append(
            CategoryDelta(
                category=cat,
                current=cur_score,
                previous=prev_score,
                delta=cur_score - prev_score,
            )
        )

    return ApiResponse(
        data=CompareResponse(
            current=current_resp,
            previous=previous_resp,
            score_delta=current_resp.score - previous_resp.score,
            category_deltas=category_deltas,
        )
    )
