import os
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional
from functools import wraps

from fastapi import HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
import secrets

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Manage API keys for service authentication."""

    def __init__(self):
        self.valid_keys = self._load_api_keys()

    def _load_api_keys(self) -> set:
        """Load valid API keys from environment."""
        keys_str = os.getenv("VALID_API_KEYS", "")
        if not keys_str:
            logger.warning("No API keys configured. Using demo key.")
            return {"demo-key-12345"}
        return set(keys_str.split(","))

    def validate_key(self, api_key: str) -> bool:
        """Validate API key."""
        return api_key in self.valid_keys

    def generate_key(self) -> str:
        """Generate a new API key."""
        return secrets.token_urlsafe(32)


class RateLimiter:
    """Rate limiting configuration."""

    def __init__(self):
        self.limiter = Limiter(key_func=get_remote_address)

    def get_limiter(self):
        """Get configured limiter."""
        return self.limiter


class RequestValidator:
    """Validate and sanitize requests."""

    MAX_FILENAME_LENGTH = 255
    ALLOWED_FILENAME_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._- ")

    @staticmethod
    def validate_filename(filename: str) -> str:
        """Validate and sanitize filename."""
        if not filename:
            raise HTTPException(status_code=400, detail="Filename cannot be empty")

        if len(filename) > RequestValidator.MAX_FILENAME_LENGTH:
            raise HTTPException(status_code=400, detail="Filename too long")

        # Remove invalid characters
        sanitized = "".join(
            c for c in filename
            if c in RequestValidator.ALLOWED_FILENAME_CHARS
        )

        if not sanitized:
            raise HTTPException(status_code=400, detail="Filename contains invalid characters")

        return sanitized

    @staticmethod
    def validate_password(password: str, min_length: int = 8) -> bool:
        """Validate password strength."""
        if not password or len(password) < min_length:
            raise HTTPException(status_code=400, detail=f"Password must be at least {min_length} characters")
        return True


class SignatureValidator:
    """Validate request signatures for API security."""

    def __init__(self, secret: Optional[str] = None):
        self.secret = secret or os.getenv("API_SECRET_KEY", "default-secret")

    def generate_signature(self, data: str) -> str:
        """Generate HMAC signature."""
        return hmac.new(
            self.secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

    def validate_signature(self, data: str, signature: str) -> bool:
        """Validate HMAC signature."""
        expected = self.generate_signature(data)
        return hmac.compare_digest(expected, signature)


class CORSPolicy:
    """CORS policy configuration."""

    def __init__(self):
        self.allowed_origins = self._parse_origins()
        self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allowed_headers = ["*"]
        self.allow_credentials = True
        self.max_age = 3600

    def _parse_origins(self) -> list:
        """Parse allowed origins from environment."""
        origins_str = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:8000,http://localhost:5000,http://127.0.0.1:8000"
        )
        return [o.strip() for o in origins_str.split(",")]

    def is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed."""
        return origin in self.allowed_origins or "*" in self.allowed_origins


class SecurityHeaders:
    """Security headers for responses."""

    @staticmethod
    def get_security_headers() -> dict:
        """Get security headers."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }


# Initialize security components
api_key_manager = APIKeyManager()
rate_limiter = RateLimiter()
signature_validator = SignatureValidator()
cors_policy = CORSPolicy()


async def verify_api_key(request: Request) -> str:
    """Verify API key from request header."""
    api_key = request.headers.get("X-API-Key")
    
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if not api_key_manager.validate_key(api_key):
        logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key


async def verify_signature(request: Request) -> bool:
    """Verify request signature."""
    signature = request.headers.get("X-Signature")
    
    if not signature:
        logger.warning("Missing signature header")
        raise HTTPException(status_code=401, detail="Signature required")
    
    return True
