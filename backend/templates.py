"""
Prompt Template Management Endpoints
Allows users to create, manage, and share prompt templates
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from .auth import get_current_active_user, User
from .database import get_db, PromptTemplateModel

router = APIRouter(prefix="/api/templates", tags=["Prompt Templates"])

@router.get("/")
async def list_templates(
    include_public: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all templates (user's own + public templates)"""
    query = db.query(PromptTemplateModel)

    if include_public:
        templates = query.filter(
            (PromptTemplateModel.user_id == current_user.id) |
            (PromptTemplateModel.is_public == True)
        ).all()
    else:
        templates = query.filter(PromptTemplateModel.user_id == current_user.id).all()

    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "content": t.content,
            "is_public": t.is_public,
            "is_owner": t.user_id == current_user.id,
            "created_at": t.created_at.isoformat(),
            "updated_at": t.updated_at.isoformat()
        }
        for t in templates
    ]

@router.post("/")
async def create_template(
    name: str,
    content: str,
    description: str = "",
    is_public: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new prompt template"""
    template = PromptTemplateModel(
        name=name,
        description=description,
        content=content,
        user_id=current_user.id,
        is_public=is_public
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "content": template.content,
        "is_public": template.is_public,
        "created_at": template.created_at.isoformat()
    }

@router.get("/{template_id}")
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific template"""
    template = db.query(PromptTemplateModel).filter(
        PromptTemplateModel.id == template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Check access: must be owner or public
    if template.user_id != current_user.id and not template.is_public:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "content": template.content,
        "is_public": template.is_public,
        "is_owner": template.user_id == current_user.id,
        "created_at": template.created_at.isoformat(),
        "updated_at": template.updated_at.isoformat()
    }

@router.put("/{template_id}")
async def update_template(
    template_id: int,
    name: str = None,
    content: str = None,
    description: str = None,
    is_public: bool = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a template (owner only)"""
    template = db.query(PromptTemplateModel).filter(
        PromptTemplateModel.id == template_id,
        PromptTemplateModel.user_id == current_user.id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found or access denied")

    if name is not None:
        template.name = name
    if content is not None:
        template.content = content
    if description is not None:
        template.description = description
    if is_public is not None:
        template.is_public = is_public

    template.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(template)

    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "content": template.content,
        "is_public": template.is_public,
        "updated_at": template.updated_at.isoformat()
    }

@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a template (owner only)"""
    template = db.query(PromptTemplateModel).filter(
        PromptTemplateModel.id == template_id,
        PromptTemplateModel.user_id == current_user.id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found or access denied")

    db.delete(template)
    db.commit()

    return {"status": "deleted", "id": template_id}

@router.post("/{template_id}/duplicate")
async def duplicate_template(
    template_id: int,
    new_name: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Duplicate a template (from public or own)"""
    original = db.query(PromptTemplateModel).filter(
        PromptTemplateModel.id == template_id
    ).first()

    if not original:
        raise HTTPException(status_code=404, detail="Template not found")

    # Check access
    if original.user_id != current_user.id and not original.is_public:
        raise HTTPException(status_code=403, detail="Access denied")

    duplicate = PromptTemplateModel(
        name=new_name,
        description=f"Duplicated from: {original.name}",
        content=original.content,
        user_id=current_user.id,
        is_public=False
    )

    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)

    return {
        "id": duplicate.id,
        "name": duplicate.name,
        "content": duplicate.content,
        "created_at": duplicate.created_at.isoformat()
    }
