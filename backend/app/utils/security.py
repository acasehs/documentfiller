"""Security middleware for rate limiting, authentication, and request validation"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict
import time
from collections import defaultdict
import re


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent abuse

    Limits:
    - 100 requests per minute per IP for general endpoints
    - 10 requests per minute per IP for generation endpoints
    - 5 requests per minute per IP for upload endpoints
    """

    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, list] = defaultdict(list)
        self.limits = {
            '/api/content/generate': (10, 60),  # 10 requests per 60 seconds
            '/api/documents/upload': (5, 60),   # 5 uploads per 60 seconds
            '/api/review': (10, 60),             # 10 reviews per 60 seconds
            'default': (100, 60),                # 100 requests per 60 seconds
        }

    async def dispatch(self, request: Request, call_next: Callable):
        """Process request with rate limiting"""

        # Get client IP
        client_ip = request.client.host

        # Find applicable rate limit
        path = request.url.path
        rate_limit = self.limits.get('default')

        for endpoint, limit in self.limits.items():
            if endpoint != 'default' and path.startswith(endpoint):
                rate_limit = limit
                break

        max_requests, window = rate_limit

        # Clean old entries
        current_time = time.time()
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < window
        ]

        # Check rate limit
        if len(self.requests[client_ip]) >= max_requests:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded. Max {max_requests} requests per {window} seconds."
                }
            )

        # Add current request
        self.requests[client_ip].append(current_time)

        # Process request
        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)

        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Validate all incoming requests for security threats"""

    # Suspicious patterns in request paths
    SUSPICIOUS_PATTERNS = [
        r'\.\.',           # Directory traversal
        r'%00',            # Null byte
        r'<script',        # XSS attempts
        r'javascript:',    # JavaScript protocol
        r'union.*select',  # SQL injection
        r'exec\s*\(',      # Command injection
    ]

    async def dispatch(self, request: Request, call_next: Callable):
        """Validate request before processing"""

        # Check request path for suspicious patterns
        path = request.url.path
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, path, re.IGNORECASE):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid request path"}
                )

        # Check request size
        content_length = request.headers.get('content-length')
        if content_length:
            max_size = 52428800  # 50MB
            if int(content_length) > max_size:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": "Request too large"}
                )

        # Process request
        response = await call_next(request)
        return response


# Authentication utilities
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthManager:
    """Manages authentication and authorization"""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = 30

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)


# CSRF Protection
import secrets


class CSRFProtection:
    """CSRF token generation and validation"""

    def __init__(self):
        self.tokens: Dict[str, float] = {}
        self.token_lifetime = 3600  # 1 hour

    def generate_token(self) -> str:
        """Generate a CSRF token"""
        token = secrets.token_urlsafe(32)
        self.tokens[token] = time.time()
        return token

    def validate_token(self, token: str) -> bool:
        """Validate a CSRF token"""
        if token not in self.tokens:
            return False

        # Check if token is expired
        if time.time() - self.tokens[token] > self.token_lifetime:
            del self.tokens[token]
            return False

        # Token is valid, remove it (one-time use)
        del self.tokens[token]
        return True

    def cleanup_expired_tokens(self):
        """Remove expired tokens"""
        current_time = time.time()
        expired = [
            token for token, timestamp in self.tokens.items()
            if current_time - timestamp > self.token_lifetime
        ]
        for token in expired:
            del self.tokens[token]
