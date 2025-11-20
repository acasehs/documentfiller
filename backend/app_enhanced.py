"""
Enhanced FastAPI Backend for DocumentFiller Web Application
With Authentication, Database, and Batch Processing
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import timedelta
import uvicorn
import json
import asyncio
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import authentication and database
from auth import (
    User, UserCreate, Token, authenticate_user, create_access_token,
    get_current_active_user, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
)
from database import (
    init_db, get_db, get_user_by_username, get_user_by_email, create_user,
    create_document, get_document_by_id, get_user_documents
)
from batch_processor import batch_processor, BatchStatus

# Import existing modules
from content_processor import ContentProcessor
from document_reviewer import DocumentReviewer

app = FastAPI(
    title="DocumentFiller API",
    description="AI-powered document generation and review system with authentication",
    version="2.0.0"
)

# Initialize database
init_db()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
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

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

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
    operation_mode: str
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
    sections: List[Dict[str, Any]]
    operation_mode: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 4000
    process_empty_only: bool = False
    client_id: str

class GenerateResponse(BaseModel):
    generated_content: str
    tokens_used: int
    model: str
    timestamp: str
    strategy_used: str

# User sessions (will be replaced with database sessions)
sessions_store: Dict[str, Dict] = {}

# ==================== Authentication Endpoints ====================

@app.post("/api/auth/register", response_model=User)
async def register(user_data: UserCreate):
    """Register a new user"""
    # Check if user exists
    existing_user = await get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    existing_email = await get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = await create_user(user_data.email, user_data.username, hashed_password)

    return user

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: LoginRequest):
    """Authenticate user and return JWT token"""
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

# ==================== Core Endpoints ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "DocumentFiller API",
        "version": "2.0.0",
        "features": ["authentication", "database", "batch_processing"]
    }

@app.post("/api/config")
async def save_config(
    config: ConfigModel,
    current_user: User = Depends(get_current_active_user)
):
    """Save API configuration for current user"""
    session_id = f"user_{current_user.id}"
    sessions_store[session_id] = {
        "user_id": current_user.id,
        "api_url": config.api_url,
        "api_key": config.api_key,
        "model": config.model,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens
    }
    return {"status": "success", "message": "Configuration saved"}

@app.get("/api/config")
async def get_config(current_user: User = Depends(get_current_active_user)):
    """Retrieve current user's configuration"""
    session_id = f"user_{current_user.id}"
    if session_id in sessions_store:
        return sessions_store[session_id]
    return {}

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Upload and parse a DOCX document"""
    try:
        from docx import Document
        import tempfile
        import uuid

        # Save uploaded file
        upload_dir = "/app/uploads" if os.path.exists("/app/uploads") else "./uploads"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Parse document
        doc = Document(file_path)
        document_id = str(uuid.uuid4())

        # Extract sections
        sections = []
        for para in doc.paragraphs:
            if para.style.name.startswith('Heading'):
                level = int(para.style.name.split()[-1]) if para.style.name.split()[-1].isdigit() else 1
                section = {
                    "id": f"section_{len(sections)}",
                    "title": para.text,
                    "level": level,
                    "content": "",
                }
                sections.append(section)
            elif sections:
                sections[-1]["content"] += para.text + "\n"

        # Store in database
        await create_document(document_id, file.filename, file_path, current_user.id)

        return {
            "document_id": document_id,
            "filename": file.filename,
            "sections": sections,
            "upload_time": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@app.get("/api/documents")
async def list_documents(current_user: User = Depends(get_current_active_user)):
    """List all documents for current user"""
    docs = await get_user_documents(current_user.id)
    return [
        {
            "document_id": doc.document_id,
            "filename": doc.filename,
            "upload_time": doc.upload_time.isoformat()
        }
        for doc in docs
    ]

@app.post("/api/generate", response_model=GenerateResponse)
async def generate_content(
    request: GenerateContentRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Generate content for a document section"""
    try:
        import requests

        session_id = f"user_{current_user.id}"
        if session_id not in sessions_store:
            raise HTTPException(status_code=400, detail="API not configured")

        config = sessions_store[session_id]

        # Build prompt
        if request.operation_mode == "REPLACE":
            system_prompt = f"Generate content for the section: {request.section_title}"
            if request.master_prompt:
                system_prompt = request.master_prompt.replace("{{SECTION_TITLE}}", request.section_title)
        elif request.operation_mode == "REWORK":
            system_prompt = f"Improve and enhance the following content for section '{request.section_title}':\n\n{request.existing_content}"
        else:
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

# ==================== Batch Processing Endpoints ====================

@app.post("/api/batch/start")
async def start_batch_processing(
    request: BatchProcessRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Start batch processing of multiple sections"""
    try:
        # Create batch task
        task_id = await batch_processor.create_task(
            document_id=request.document_id,
            sections=request.sections,
            operation_mode=request.operation_mode,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            process_empty_only=request.process_empty_only,
            client_id=request.client_id
        )

        # Define generate callback
        async def generate_callback(**kwargs):
            gen_request = GenerateContentRequest(**kwargs)
            result = await generate_content(gen_request, current_user)
            return result.dict()

        # Start task
        await batch_processor.start_task(task_id, manager, generate_callback)

        return {
            "task_id": task_id,
            "status": "started",
            "sections_count": len(request.sections)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@app.get("/api/batch/{task_id}/status")
async def get_batch_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get status of a batch processing task"""
    try:
        status = await batch_processor.get_task_status(task_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/batch/{task_id}/pause")
async def pause_batch(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Pause a running batch task"""
    try:
        await batch_processor.pause_task(task_id)
        return {"status": "paused"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/batch/{task_id}/resume")
async def resume_batch(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Resume a paused batch task"""
    try:
        async def generate_callback(**kwargs):
            gen_request = GenerateContentRequest(**kwargs)
            result = await generate_content(gen_request, current_user)
            return result.dict()

        await batch_processor.resume_task(task_id, manager, generate_callback)
        return {"status": "resumed"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/batch/{task_id}/cancel")
async def cancel_batch(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Cancel a batch task"""
    try:
        await batch_processor.cancel_task(task_id)
        return {"status": "cancelled"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== WebSocket ====================

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_message({
                "type": "ack",
                "message": "Message received",
                "timestamp": datetime.now().isoformat()
            }, client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)

# ==================== Other Endpoints ====================

@app.post("/api/review")
async def review_content(
    request: ReviewRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Review content quality"""
    try:
        reviewer = DocumentReviewer()
        review_result = reviewer.review_section(
            content=request.content,
            section_title=request.section_title
        )
        return review_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")

@app.get("/api/models")
async def get_available_models(current_user: User = Depends(get_current_active_user)):
    """Get list of available models from OpenWebUI"""
    try:
        session_id = f"user_{current_user.id}"
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
