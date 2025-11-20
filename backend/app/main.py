"""
FastAPI Backend for Document Filler Web Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from pathlib import Path

from app.api.routes import documents, content, review, config
from app.utils.config import settings

# Ensure upload directory exists
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the application"""
    # Startup
    print("🚀 Document Filler Web API starting up...")
    print(f"📁 Upload directory: {UPLOAD_DIR}")
    print(f"🔗 OpenWebUI URL: {settings.OPENWEBUI_BASE_URL}")

    yield

    # Shutdown
    print("👋 Document Filler Web API shutting down...")


app = FastAPI(
    title="Document Filler API",
    description="AI-powered document content generation and analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for serving files
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Include routers
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(review.router, prefix="/api/review", tags=["review"])
app.include_router(config.router, prefix="/api/config", tags=["config"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Document Filler Web API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "upload_dir": str(UPLOAD_DIR),
        "openwebui_configured": bool(settings.OPENWEBUI_BASE_URL)
    }
