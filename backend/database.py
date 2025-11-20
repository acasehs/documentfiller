"""
Database Module
SQLAlchemy models and database operations
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./documentfiller.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()

# Models
class UserModel(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    documents = relationship("DocumentModel", back_populates="owner")
    sessions = relationship("SessionModel", back_populates="user")

class DocumentModel(Base):
    """Document model"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, unique=True, index=True, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    owner = relationship("UserModel", back_populates="documents")
    sections = relationship("SectionModel", back_populates="document", cascade="all, delete-orphan")

class SectionModel(Base):
    """Document section model"""
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(String, index=True, nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"))
    title = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    content = Column(Text, default="")
    generated_content = Column(Text, default="")
    parent_id = Column(Integer, ForeignKey("sections.id"), nullable=True)
    edit_count = Column(Integer, default=0)
    last_modified = Column(DateTime, default=datetime.utcnow)
    model_used = Column(String, nullable=True)

    # Relationships
    document = relationship("DocumentModel", back_populates="sections")
    children = relationship("SectionModel", back_populates="parent")
    parent = relationship("SectionModel", back_populates="children", remote_side=[id])

class SessionModel(Base):
    """User session model for configuration storage"""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    api_url = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    model = Column(String, nullable=True)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=4000)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("UserModel", back_populates="sessions")

class PromptTemplateModel(Base):
    """Prompt template model"""
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GenerationHistoryModel(Base):
    """Generation history model"""
    __tablename__ = "generation_history"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"))
    prompt = Column(Text, nullable=False)
    generated_content = Column(Text, nullable=False)
    model = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)
    tokens_used = Column(Integer, nullable=True)
    operation_mode = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ReviewHistoryModel(Base):
    """Review history model"""
    __tablename__ = "review_history"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"))
    content = Column(Text, nullable=False)
    cohesion_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    accuracy_score = Column(Float, nullable=True)
    veracity_score = Column(Float, nullable=True)
    completeness_score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
def init_db():
    """Initialize the database"""
    Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User operations
async def get_user_by_username(username: str):
    """Get user by username"""
    db = SessionLocal()
    try:
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if user:
            from .auth import User
            return User(
                id=user.id,
                email=user.email,
                username=user.username,
                is_active=user.is_active,
                created_at=user.created_at
            )
        return None
    finally:
        db.close()

async def get_user_by_email(email: str):
    """Get user by email"""
    db = SessionLocal()
    try:
        user = db.query(UserModel).filter(UserModel.email == email).first()
        return user
    finally:
        db.close()

async def create_user(email: str, username: str, hashed_password: str):
    """Create a new user"""
    db = SessionLocal()
    try:
        user = UserModel(
            email=email,
            username=username,
            hashed_password=hashed_password
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        from .auth import User
        return User(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at
        )
    finally:
        db.close()

# Document operations
async def create_document(document_id: str, filename: str, file_path: str, user_id: int):
    """Create a new document"""
    db = SessionLocal()
    try:
        doc = DocumentModel(
            document_id=document_id,
            filename=filename,
            file_path=file_path,
            user_id=user_id
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc
    finally:
        db.close()

async def get_document_by_id(document_id: str, user_id: int):
    """Get document by ID"""
    db = SessionLocal()
    try:
        doc = db.query(DocumentModel).filter(
            DocumentModel.document_id == document_id,
            DocumentModel.user_id == user_id
        ).first()
        return doc
    finally:
        db.close()

async def get_user_documents(user_id: int):
    """Get all documents for a user"""
    db = SessionLocal()
    try:
        docs = db.query(DocumentModel).filter(DocumentModel.user_id == user_id).all()
        return docs
    finally:
        db.close()
