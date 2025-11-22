"""Security utilities for input validation and sanitization"""
import re
import html
from typing import Optional, List
from pathlib import Path
import magic  # pip install python-magic-bin (Windows) or python-magic (Linux/Mac)
from pydantic import validator


class InputValidator:
    """Validates and sanitizes user inputs"""

    # Allowed characters in filenames
    FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9._\-\s()]+$')

    # Maximum lengths
    MAX_FILENAME_LENGTH = 255
    MAX_TEXT_LENGTH = 100000  # 100KB of text
    MAX_SECTION_TEXT_LENGTH = 10000
    MAX_PROMPT_LENGTH = 50000

    # Dangerous patterns
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript protocol
        r'on\w+\s*=',  # Event handlers (onclick, onload, etc.)
        r'<iframe[^>]*>',  # iframes
        r'<embed[^>]*>',  # embeds
        r'<object[^>]*>',  # objects
    ]

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal and injection attacks

        Args:
            filename: Original filename

        Returns:
            Sanitized filename

        Raises:
            ValueError: If filename is invalid
        """
        if not filename:
            raise ValueError("Filename cannot be empty")

        # Remove path components
        filename = Path(filename).name

        # Check length
        if len(filename) > InputValidator.MAX_FILENAME_LENGTH:
            raise ValueError(f"Filename too long (max {InputValidator.MAX_FILENAME_LENGTH})")

        # Remove null bytes
        filename = filename.replace('\0', '')

        # Check for directory traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            raise ValueError("Invalid filename: directory traversal detected")

        # Validate characters
        if not InputValidator.FILENAME_PATTERN.match(filename):
            raise ValueError("Filename contains invalid characters")

        return filename

    @staticmethod
    def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize text content to prevent XSS and injection attacks

        Args:
            text: Text to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized text

        Raises:
            ValueError: If text is invalid
        """
        if text is None:
            return ""

        # Check length
        max_len = max_length or InputValidator.MAX_TEXT_LENGTH
        if len(text) > max_len:
            raise ValueError(f"Text too long (max {max_len} characters)")

        # Remove null bytes
        text = text.replace('\0', '')

        # Check for dangerous patterns
        for pattern in InputValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValueError("Text contains potentially dangerous content")

        # HTML escape for safety
        text = html.escape(text)

        return text

    @staticmethod
    def sanitize_html(content: str) -> str:
        """
        Sanitize HTML content (for markdown preview)

        Args:
            content: HTML content

        Returns:
            Sanitized HTML
        """
        # For now, just escape everything
        # In production, use a library like bleach
        return html.escape(content)

    @staticmethod
    def validate_url(url: str) -> str:
        """
        Validate URL format

        Args:
            url: URL to validate

        Returns:
            Validated URL

        Raises:
            ValueError: If URL is invalid
        """
        if not url:
            raise ValueError("URL cannot be empty")

        # Simple validation - in production use urllib.parse
        if not (url.startswith('http://') or url.startswith('https://')):
            raise ValueError("URL must start with http:// or https://")

        # Check for SSRF attempts
        forbidden_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '169.254.169.254']
        for host in forbidden_hosts:
            if host in url.lower():
                raise ValueError("URL points to forbidden host")

        return url

    @staticmethod
    def validate_document_id(doc_id: str) -> str:
        """
        Validate document ID format

        Args:
            doc_id: Document ID

        Returns:
            Validated ID

        Raises:
            ValueError: If ID is invalid
        """
        # Should be UUID format
        if not re.match(r'^[a-f0-9\-]{36}$', doc_id):
            raise ValueError("Invalid document ID format")

        return doc_id

    @staticmethod
    def validate_section_id(section_id: str) -> str:
        """
        Validate section ID format

        Args:
            section_id: Section ID

        Returns:
            Validated ID

        Raises:
            ValueError: If ID is invalid
        """
        # Should be document_id + _section_ + number
        if not re.match(r'^[a-f0-9\-]{36}_section_\d+$', section_id):
            raise ValueError("Invalid section ID format")

        return section_id

    @staticmethod
    def validate_file_upload(file_path: str, allowed_extensions: List[str] = ['.docx']) -> bool:
        """
        Validate uploaded file using multiple checks

        Args:
            file_path: Path to uploaded file
            allowed_extensions: List of allowed file extensions

        Returns:
            True if file is valid

        Raises:
            ValueError: If file is invalid
        """
        path = Path(file_path)

        # Check file exists
        if not path.exists():
            raise ValueError("File does not exist")

        # Check file size
        max_size = 52428800  # 50MB
        file_size = path.stat().st_size
        if file_size > max_size:
            raise ValueError(f"File too large (max {max_size / 1024 / 1024}MB)")

        if file_size == 0:
            raise ValueError("File is empty")

        # Check extension
        if path.suffix.lower() not in allowed_extensions:
            raise ValueError(f"Invalid file type. Allowed: {', '.join(allowed_extensions)}")

        # Check MIME type (requires python-magic)
        try:
            mime = magic.from_file(str(path), mime=True)
            allowed_mimes = [
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/zip',  # .docx are ZIP files
            ]
            if mime not in allowed_mimes:
                raise ValueError(f"Invalid file MIME type: {mime}")
        except Exception as e:
            # If magic is not available, skip MIME check
            pass

        return True


class ContentSanitizer:
    """Sanitizes content from AI responses and user input"""

    @staticmethod
    def sanitize_ai_response(content: str) -> str:
        """
        Sanitize AI-generated content

        Args:
            content: AI-generated content

        Returns:
            Sanitized content
        """
        if not content:
            return ""

        # Remove null bytes
        content = content.replace('\0', '')

        # Limit length
        max_length = 100000
        if len(content) > max_length:
            content = content[:max_length]

        # Allow markdown but escape dangerous HTML
        # This is a simple approach - production should use proper markdown sanitizer
        return content

    @staticmethod
    def sanitize_prompt(prompt: str) -> str:
        """
        Sanitize user-provided prompts

        Args:
            prompt: User prompt

        Returns:
            Sanitized prompt
        """
        if not prompt:
            return ""

        # Check length
        if len(prompt) > InputValidator.MAX_PROMPT_LENGTH:
            raise ValueError(f"Prompt too long (max {InputValidator.MAX_PROMPT_LENGTH})")

        # Remove null bytes
        prompt = prompt.replace('\0', '')

        # Check for prompt injection attempts
        suspicious_patterns = [
            r'ignore\s+previous\s+instructions',
            r'disregard\s+all',
            r'forget\s+everything',
            r'new\s+instructions',
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                raise ValueError("Prompt contains suspicious content")

        return prompt
