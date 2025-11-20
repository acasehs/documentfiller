"""Content generation API endpoints"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict
import asyncio
import json

from app.models.content import (
    ContentGenerationRequest,
    ContentGenerationResponse,
    ModelComparisonRequest,
    ModelComparisonResponse,
)
from app.services.content_service import ContentService

router = APIRouter()
content_service = ContentService()

# Store active WebSocket connections for real-time updates
active_connections: Dict[str, WebSocket] = {}


@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(request: ContentGenerationRequest):
    """
    Generate content for a document section using AI

    Supports three modes:
    - replace: Generate new content from scratch
    - rework: Enhance/rewrite existing content
    - append: Add to existing content
    """
    try:
        result = await content_service.generate_content(request)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document or section not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")


@router.post("/compare-models", response_model=ModelComparisonResponse)
async def compare_models(request: ModelComparisonRequest):
    """
    Compare content generation across multiple AI models

    Useful for evaluating which model produces better results for specific content
    """
    try:
        result = await content_service.compare_models(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model comparison failed: {str(e)}")


@router.websocket("/ws/generate/{client_id}")
async def websocket_generate(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time content generation with status updates

    The client receives:
    - status: Current operation status
    - progress: Percentage complete (0-100)
    - message: Human-readable status message
    - result: Final generated content (on completion)
    """
    await websocket.accept()
    active_connections[client_id] = websocket

    try:
        while True:
            # Receive generation request
            data = await websocket.receive_text()
            request_data = json.loads(data)

            # Convert to ContentGenerationRequest
            request = ContentGenerationRequest(**request_data)

            # Generate content with status callbacks
            async def status_callback(status: str, progress: int, message: str):
                """Send status updates to client"""
                try:
                    await websocket.send_json({
                        "type": "status",
                        "status": status,
                        "progress": progress,
                        "message": message
                    })
                except Exception:
                    pass

            try:
                result = await content_service.generate_content(
                    request,
                    status_callback=status_callback
                )

                # Send final result
                await websocket.send_json({
                    "type": "result",
                    "data": result.model_dump()
                })

            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })

    except WebSocketDisconnect:
        if client_id in active_connections:
            del active_connections[client_id]
    except Exception as e:
        print(f"WebSocket error: {e}")
        if client_id in active_connections:
            del active_connections[client_id]


@router.get("/models")
async def list_available_models():
    """
    List available AI models from OpenWebUI

    Returns model names and capabilities
    """
    try:
        models = await content_service.get_available_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")


@router.get("/knowledge-collections")
async def list_knowledge_collections():
    """
    List available knowledge collections (RAG) from OpenWebUI

    Returns collection IDs and names for use in content generation
    """
    try:
        collections = await content_service.get_knowledge_collections()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch collections: {str(e)}")
