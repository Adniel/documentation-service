"""Security utilities for password hashing and JWT tokens."""

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from src.config import get_settings

settings = get_settings()

# Password hashing context using argon2 (more secure than bcrypt, no 72-byte limit)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(user_id: str, jti: str | None = None) -> str:
    """Create a JWT access token.

    Args:
        user_id: User ID to encode in token
        jti: Optional JWT Token ID for session tracking. If not provided,
             session validation will be skipped (for backwards compatibility).
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "type": "access",
    }
    if jti:
        to_encode["jti"] = jti
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(user_id: str) -> str:
    """Create a JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict | None:
    """Decode a JWT token. Returns None if invalid."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except jwt.JWTError:
        return None


def create_token_pair(user_id: str, jti: str | None = None) -> tuple[str, str]:
    """Create both access and refresh tokens.

    Args:
        user_id: User ID to encode in tokens
        jti: Optional JWT Token ID for session tracking
    """
    access_token = create_access_token(user_id, jti)
    refresh_token = create_refresh_token(user_id)
    return access_token, refresh_token


def extract_jti(token: str) -> str | None:
    """Extract JTI from a JWT token without full validation.

    Returns:
        JTI if present, None otherwise
    """
    payload = decode_token(token)
    if payload:
        return payload.get("jti")
    return None
