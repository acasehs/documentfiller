"""Document-related Pydantic models"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class DocumentComment(BaseModel):
    """Represents a comment in a Word document"""
    author: str
    text: str
    date: Optional[datetime] = None


class DocumentSection(BaseModel):
    """Represents a section in the document hierarchy"""
    id: str = Field(..., description="Unique identifier for the section")
    level: int = Field(..., ge=1, le=6, description="Heading level (1-6)")
    text: str = Field(..., description="Section heading text")
    full_path: str = Field(..., description="Full hierarchical path")
    has_content: bool = Field(default=False, description="Whether section has content")
    existing_content: str = Field(default="", description="Existing content in section")
    children: List["DocumentSection"] = Field(default_factory=list, description="Child sections")
    comments: List[DocumentComment] = Field(default_factory=list, description="Associated comments")
    section_hash: str = Field(..., description="Hash of section for tracking changes")


class DocumentStructure(BaseModel):
    """Complete document structure"""
    filename: str
    total_sections: int
    sections: List[DocumentSection]
    has_comments: bool = False
    total_comments: int = 0


class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    document_id: str
    filename: str
    size: int
    structure: DocumentStructure
    message: str = "Document uploaded and parsed successfully"


class DocumentSaveRequest(BaseModel):
    """Request to save document with updates"""
    document_id: str
    sections_to_update: Dict[str, str] = Field(
        ...,
        description="Map of section_id to new content"
    )
    backup: bool = Field(default=True, description="Create backup before saving")


class DocumentSaveResponse(BaseModel):
    """Response after saving document"""
    success: bool
    message: str
    backup_path: Optional[str] = None
    updated_sections: int
