"""Document review and analysis API endpoints"""
from fastapi import APIRouter, HTTPException

from app.models.review import (
    ReviewRequest,
    ReviewResponse,
    TenseAnalysisRequest,
    TenseAnalysisResponse,
)
from app.services.review_service import ReviewService

router = APIRouter()
review_service = ReviewService()


@router.post("/conduct", response_model=ReviewResponse)
async def conduct_review(request: ReviewRequest):
    """
    Conduct a comprehensive technical review of a section or entire document

    Analyzes:
    - Cohesion and flow
    - Clarity and readability
    - Technical accuracy
    - Factual veracity
    - Completeness

    Returns structured feedback with scores and recommendations
    """
    try:
        result = await review_service.conduct_review(request)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document or section not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")


@router.post("/analyze-tenses", response_model=TenseAnalysisResponse)
async def analyze_tenses(request: TenseAnalysisRequest):
    """
    Analyze tense consistency in a section or entire document

    Detects:
    - Primary tense used
    - Tense inconsistencies
    - Suggested corrections

    Useful for technical writing that requires consistent past/present tense
    """
    try:
        result = await review_service.analyze_tenses(request)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document or section not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tense analysis failed: {str(e)}")


@router.post("/apply-suggestions/{document_id}/{section_id}")
async def apply_review_suggestions(
    document_id: str,
    section_id: str,
    suggestion_ids: list[int]
):
    """
    Apply specific review suggestions to a section

    Automatically implements the recommended changes
    """
    try:
        result = await review_service.apply_suggestions(
            document_id,
            section_id,
            suggestion_ids
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply suggestions: {str(e)}")


@router.get("/readability/{document_id}/{section_id}")
async def get_readability_metrics(document_id: str, section_id: str):
    """
    Get readability metrics for a section

    Returns:
    - Flesch Reading Ease score
    - Flesch-Kincaid Grade Level
    - Word count and sentence statistics
    """
    try:
        metrics = await review_service.get_readability_metrics(document_id, section_id)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
