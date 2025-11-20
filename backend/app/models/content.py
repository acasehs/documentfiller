"""Content generation models"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class OperationMode(str, Enum):
    """Content generation operation modes"""
    REPLACE = "replace"
    REWORK = "rework"
    APPEND = "append"


class ContentGenerationRequest(BaseModel):
    """Request to generate content for a section"""
    document_id: str
    section_id: str
    mode: OperationMode = OperationMode.REPLACE

    # AI Configuration
    model: str = "llama3.2:latest"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=100, le=100000)

    # Optional overrides
    custom_prompt: Optional[str] = None
    knowledge_collections: List[str] = Field(default_factory=list)
    use_master_prompt: bool = True

    # Context options
    include_document_context: bool = True
    include_comments: bool = True


class ContentGenerationResponse(BaseModel):
    """Response from content generation"""
    section_id: str
    generated_content: str
    prompt_used: str
    model: str
    tokens_used: Optional[int] = None
    processing_time: float
    success: bool = True
    error: Optional[str] = None


class ModelComparisonRequest(BaseModel):
    """Request to compare multiple models"""
    document_id: str
    section_id: str
    models: List[str] = Field(..., min_items=2, max_items=5)
    mode: OperationMode = OperationMode.REPLACE
    temperature: float = 0.7
    max_tokens: int = 2000


class ModelComparisonResult(BaseModel):
    """Result from a single model in comparison"""
    model: str
    content: str
    processing_time: float
    error: Optional[str] = None


class ModelComparisonResponse(BaseModel):
    """Response from model comparison"""
    section_id: str
    results: List[ModelComparisonResult]
    prompt_used: str
