"""
FastAPI Backend for DocumentFiller Web Application
Provides REST API and WebSocket endpoints for document generation
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import json
import asyncio
from datetime import datetime
import sys
import os

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from content_processor import ContentProcessor
from document_reviewer import DocumentReviewer
from credential_manager import CredentialManager

app = FastAPI(
    title="DocumentFiller API",
    description="AI-powered document generation and review system",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()

# Pydantic models for request/response
class ConfigModel(BaseModel):
    api_url: str
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 4000

class GenerateContentRequest(BaseModel):
    section_id: str
    section_title: str
    existing_content: str
    operation_mode: str  # REPLACE, REWORK, APPEND
    model: str
    temperature: float = 0.7
    max_tokens: int = 4000
    use_rag: bool = False
    knowledge_collection: Optional[str] = None
    master_prompt: Optional[str] = None

class ReviewRequest(BaseModel):
    content: str
    section_title: str

class BatchProcessRequest(BaseModel):
    document_id: str
    sections: List[str]
    operation_mode: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 4000
    process_empty_only: bool = False

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    sections: List[Dict[str, Any]]
    upload_time: str

class GenerateResponse(BaseModel):
    generated_content: str
    tokens_used: int
    model: str
    timestamp: str
    strategy_used: str

# In-memory storage (replace with database in production)
documents_store: Dict[str, Any] = {}
sessions_store: Dict[str, Dict] = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "DocumentFiller API",
        "version": "1.0.0"
    }

@app.post("/api/config")
async def save_config(config: ConfigModel):
    """Save API configuration"""
    try:
        # Use credential manager to securely store config
        cred_manager = CredentialManager()

        config_data = {
            "api_url": config.api_url,
            "api_key": config.api_key,
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens
        }

        # Store in session (in production, use proper session management)
        session_id = "default"  # TODO: Implement proper session management
        sessions_store[session_id] = config_data

        return {"status": "success", "message": "Configuration saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
async def get_config():
    """Retrieve current configuration"""
    session_id = "default"
    if session_id in sessions_store:
        return sessions_store[session_id]
    return {}

@app.post("/api/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and parse a DOCX document"""
    try:
        from docx import Document
        import tempfile
        import uuid

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Parse document
        doc = Document(tmp_path)
        document_id = str(uuid.uuid4())

        # Extract sections
        sections = []
        current_section = None

        for para in doc.paragraphs:
            if para.style.name.startswith('Heading'):
                level = int(para.style.name.split()[-1]) if para.style.name.split()[-1].isdigit() else 1
                section = {
                    "id": f"section_{len(sections)}",
                    "title": para.text,
                    "level": level,
                    "content": "",
                    "children": []
                }
                sections.append(section)
                current_section = section
            elif current_section:
                current_section["content"] += para.text + "\n"

        # Store document
        documents_store[document_id] = {
            "id": document_id,
            "filename": file.filename,
            "path": tmp_path,
            "sections": sections,
            "upload_time": datetime.now().isoformat()
        }

        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            sections=sections,
            upload_time=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@app.get("/api/documents/{document_id}")
async def get_document(document_id: str):
    """Retrieve document metadata and sections"""
    if document_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    return documents_store[document_id]

@app.post("/api/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateContentRequest):
    """Generate content for a document section"""
    try:
        import requests

        # Get API configuration
        session_id = "default"
        if session_id not in sessions_store:
            raise HTTPException(status_code=400, detail="API not configured")

        config = sessions_store[session_id]

        # Build prompt based on operation mode
        if request.operation_mode == "REPLACE":
            system_prompt = f"Generate content for the section: {request.section_title}"
            if request.master_prompt:
                system_prompt = request.master_prompt.replace("{{SECTION_TITLE}}", request.section_title)
        elif request.operation_mode == "REWORK":
            system_prompt = f"Improve and enhance the following content for section '{request.section_title}':\n\n{request.existing_content}"
        else:  # APPEND
            system_prompt = f"Add additional content to expand section '{request.section_title}'. Existing content:\n\n{request.existing_content}"

        # Call OpenWebUI API
        api_url = f"{config['api_url']}/api/chat/completions"
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": request.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate content for: {request.section_title}"}
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }

        # Add RAG if requested
        if request.use_rag and request.knowledge_collection:
            payload["files"] = [{"type": "collection", "id": request.knowledge_collection}]

        response = requests.post(api_url, headers=headers, json=payload, timeout=300)
        response.raise_for_status()

        result = response.json()
        generated_content = result['choices'][0]['message']['content']
        tokens_used = result.get('usage', {}).get('total_tokens', 0)

        return GenerateResponse(
            generated_content=generated_content,
            tokens_used=tokens_used,
            model=request.model,
            timestamp=datetime.now().isoformat(),
            strategy_used="full_prompt" if not request.use_rag else "rag"
        )

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"API call failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/api/review")
async def review_content(request: ReviewRequest):
    """Review content quality and provide feedback"""
    try:
        reviewer = DocumentReviewer()

        # Perform review
        review_result = reviewer.review_section(
            content=request.content,
            section_title=request.section_title
        )

        return review_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates during batch processing"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            await manager.send_message({
                "type": "ack",
                "message": "Message received",
                "timestamp": datetime.now().isoformat()
            }, client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)

@app.post("/api/batch/process")
async def batch_process(request: BatchProcessRequest):
    """Start batch processing of multiple sections"""
    try:
        # This would be handled asynchronously with WebSocket updates
        # For now, return a task ID
        task_id = f"batch_{datetime.now().timestamp()}"

        # In production, this would be handled by a background task queue (Celery, RQ, etc.)
        return {
            "task_id": task_id,
            "status": "started",
            "sections_count": len(request.sections)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@app.get("/api/models")
async def get_available_models():
    """Get list of available models from OpenWebUI"""
    try:
        session_id = "default"
        if session_id not in sessions_store:
            raise HTTPException(status_code=400, detail="API not configured")

        config = sessions_store[session_id]

        import requests
        response = requests.get(
            f"{config['api_url']}/api/models",
            headers={"Authorization": f"Bearer {config['api_key']}"},
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")

@app.get("/api/collections")
async def get_knowledge_collections():
    """Get list of available knowledge collections"""
    try:
        session_id = "default"
        if session_id not in sessions_store:
            raise HTTPException(status_code=400, detail="API not configured")

        config = sessions_store[session_id]

        import requests
        response = requests.get(
            f"{config['api_url']}/api/knowledge",
            headers={"Authorization": f"Bearer {config['api_key']}"},
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch collections: {str(e)}")

@app.post("/api/documents/{document_id}/commit")
async def commit_changes(document_id: str, section_id: str, content: str):
    """Commit generated content back to the document"""
    try:
        if document_id not in documents_store:
            raise HTTPException(status_code=404, detail="Document not found")

        doc_data = documents_store[document_id]

        # Find and update section
        for section in doc_data["sections"]:
            if section["id"] == section_id:
                section["content"] = content
                section["last_modified"] = datetime.now().isoformat()
                break

        # In production, save back to DOCX file
        # For now, just update in memory

        return {"status": "success", "message": "Content committed"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Commit failed: {str(e)}")

@app.get("/api/documents/{document_id}/download")
async def download_document(document_id: str):
    """Download the modified document"""
    if document_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")

    doc_data = documents_store[document_id]

    # Return the document file
    return FileResponse(
        doc_data["path"],
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=doc_data["filename"]
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
