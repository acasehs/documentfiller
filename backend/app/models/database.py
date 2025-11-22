"""Database models with encryption for sensitive fields"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from app.utils.encryption import EncryptedString

Base = declarative_base()


class User(Base):
    """User model with encrypted sensitive fields"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)  # Already hashed, no need to encrypt
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("DocumentMeta", back_populates="user", cascade="all, delete-orphan")


class APIKey(Base):
    """API keys with encrypted storage"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)  # Key description
    key_hash = Column(String(255), nullable=False)  # Hashed key for verification
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="api_keys")


class DocumentMeta(Base):
    """Document metadata with file path encryption"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(36), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(EncryptedString(500), nullable=False)  # Encrypted path
    file_size = Column(Integer, nullable=False)
    total_sections = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="documents")


class Configuration(Base):
    """Application configuration with encrypted sensitive values"""
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for global config
    key = Column(String(100), nullable=False, index=True)
    value = Column(EncryptedString(1000), nullable=False)  # Encrypted value
    is_sensitive = Column(Boolean, default=False)  # Flag for extra sensitive data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """Security audit log - tracks all sensitive operations"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # e.g., "document_upload", "content_generate"
    resource_type = Column(String(50), nullable=True)  # e.g., "document", "api_key"
    resource_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False)  # success, failure, error
    details = Column(Text, nullable=True)  # JSON with additional details
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class RateLimitEntry(Base):
    """Rate limiting tracking (can also use Redis in production)"""
    __tablename__ = "rate_limits"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(100), nullable=False, index=True)  # IP or user_id
    endpoint = Column(String(200), nullable=False)
    request_count = Column(Integer, default=1)
    window_start = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database initialization
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager


class Database:
    """Database connection and session management"""

    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Dependency for FastAPI
from app.utils.config import settings

db = Database(settings.DATABASE_URL.replace('sqlite+aiosqlite:', 'sqlite:'))


def get_db():
    """FastAPI dependency for database sessions"""
    with db.get_session() as session:
        yield session
