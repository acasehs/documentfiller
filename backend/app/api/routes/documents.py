"""Document management API endpoints"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List
import shutil
from pathlib import Path
import uuid

from app.models.document import (
    DocumentUploadResponse,
    DocumentStructure,
    DocumentSaveRequest,
    DocumentSaveResponse,
)
from app.services.document_service import DocumentService
from app.utils.config import settings

router = APIRouter()
document_service = DocumentService()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a Word document (.docx) and parse its structure

    Returns:
        Document structure with sections, headings, and existing content
    """
    # Validate file type
    if not file.filename.endswith('.docx'):
        raise HTTPException(
            status_code=400,
            detail="Only .docx files are supported"
        )

    # Generate unique document ID
    document_id = str(uuid.uuid4())

    # Save uploaded file
    upload_path = Path(settings.UPLOAD_DIR) / f"{document_id}_{file.filename}"

    try:
        with upload_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save uploaded file: {str(e)}"
        )

    # Parse document structure
    try:
        structure = await document_service.parse_document(str(upload_path), document_id)

        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            size=upload_path.stat().st_size,
            structure=structure
        )
    except Exception as e:
        # Clean up on error
        upload_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse document: {str(e)}"
        )


@router.get("/{document_id}/structure", response_model=DocumentStructure)
async def get_document_structure(document_id: str):
    """Get the structure of an uploaded document"""
    try:
        structure = await document_service.get_structure(document_id)
        if not structure:
            raise HTTPException(status_code=404, detail="Document not found")
        return structure
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{document_id}/save", response_model=DocumentSaveResponse)
async def save_document(
    document_id: str,
    request: DocumentSaveRequest,
    background_tasks: BackgroundTasks
):
    """
    Save updates to document sections

    Creates a backup if requested and applies content updates
    """
    try:
        result = await document_service.save_document(
            document_id=document_id,
            sections_to_update=request.sections_to_update,
            create_backup=request.backup
        )
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save document: {str(e)}")


@router.get("/{document_id}/download")
async def download_document(document_id: str):
    """Download the current version of the document"""
    try:
        file_path = await document_service.get_document_path(document_id)
        if not file_path or not Path(file_path).exists():
            raise HTTPException(status_code=404, detail="Document not found")

        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path,
            filename=Path(file_path).name,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its associated files"""
    try:
        result = await document_service.delete_document(document_id)
        return {"success": result, "message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
