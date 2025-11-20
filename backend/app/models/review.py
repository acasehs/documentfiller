"""Document review models"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class ReviewMetrics(BaseModel):
    """Review scoring metrics"""
    cohesion: float = Field(..., ge=0.0, le=10.0)
    clarity: float = Field(..., ge=0.0, le=10.0)
    technical_accuracy: float = Field(..., ge=0.0, le=10.0)
    factual_veracity: float = Field(..., ge=0.0, le=10.0)
    completeness: float = Field(..., ge=0.0, le=10.0)
    overall_score: float = Field(..., ge=0.0, le=10.0)


class ReviewFeedback(BaseModel):
    """Structured feedback from review"""
    category: str
    issue: str
    suggestion: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    location: Optional[str] = None


class ReviewRequest(BaseModel):
    """Request to review a section or document"""
    document_id: str
    section_id: Optional[str] = None  # None = review entire document
    use_rag: bool = True
    knowledge_collections: List[str] = Field(default_factory=list)


class ReviewResponse(BaseModel):
    """Response from document review"""
    section_id: Optional[str]
    metrics: ReviewMetrics
    feedback: List[ReviewFeedback]
    summary: str
    recommendations: List[str]
    processing_time: float


class TenseAnalysisRequest(BaseModel):
    """Request for tense analysis"""
    document_id: str
    section_id: Optional[str] = None


class TenseIssue(BaseModel):
    """Individual tense inconsistency issue"""
    location: str
    current_text: str
    detected_tense: str
    suggested_correction: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class TenseAnalysisResponse(BaseModel):
    """Response from tense analysis"""
    section_id: Optional[str]
    primary_tense: str
    issues: List[TenseIssue]
    total_issues: int
    consistency_score: float = Field(..., ge=0.0, le=100.0)
