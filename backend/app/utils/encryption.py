"""Database encryption utilities for sensitive data"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Optional


class FieldEncryption:
    """Encrypts sensitive database fields"""

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize field encryption

        Args:
            secret_key: Encryption key (uses SECRET_KEY from settings if not provided)
        """
        if secret_key is None:
            from app.utils.config import settings
            secret_key = settings.SECRET_KEY

        # Derive encryption key from secret
        self.cipher = self._create_cipher(secret_key)

    def _create_cipher(self, secret_key: str) -> Fernet:
        """
        Create Fernet cipher from secret key

        Args:
            secret_key: Secret key string

        Returns:
            Fernet cipher instance
        """
        # Use PBKDF2 to derive a proper encryption key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'documentfiller_salt',  # In production, use a random salt per installation
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        return Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string value

        Args:
            plaintext: Plain text to encrypt

        Returns:
            Encrypted string (base64 encoded)
        """
        if not plaintext:
            return ""

        encrypted = self.cipher.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a string value

        Args:
            ciphertext: Encrypted string (base64 encoded)

        Returns:
            Decrypted plain text

        Raises:
            ValueError: If decryption fails
        """
        if not ciphertext:
            return ""

        try:
            encrypted = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")


# Global encryption instance
_encryption_instance = None


def get_encryption() -> FieldEncryption:
    """Get global encryption instance (singleton)"""
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = FieldEncryption()
    return _encryption_instance


# Encrypted field type for SQLAlchemy
from sqlalchemy import TypeDecorator, String


class EncryptedString(TypeDecorator):
    """
    SQLAlchemy custom type for encrypted strings

    Usage:
        api_key = Column(EncryptedString(255))
    """

    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Encrypt value before storing in database"""
        if value is not None:
            return get_encryption().encrypt(value)
        return value

    def process_result_value(self, value, dialect):
        """Decrypt value when reading from database"""
        if value is not None:
            return get_encryption().decrypt(value)
        return value


# Hashing utilities for passwords
import hashlib
import secrets


class PasswordHasher:
    """Secure password hashing"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using PBKDF2

        Args:
            password: Plain text password

        Returns:
            Hashed password with salt
        """
        salt = secrets.token_hex(16)
        pwdhash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return salt + ':' + pwdhash.hex()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify a password against a hash

        Args:
            password: Plain text password to verify
            hashed: Stored hash

        Returns:
            True if password matches
        """
        try:
            salt, pwdhash = hashed.split(':')
            check_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return check_hash.hex() == pwdhash
        except Exception:
            return False


# API Key management
class APIKeyManager:
    """Manages API keys securely"""

    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure random API key"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash an API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    def verify_api_key(api_key: str, hashed: str) -> bool:
        """Verify an API key against its hash"""
        return hashlib.sha256(api_key.encode()).hexdigest() == hashed
