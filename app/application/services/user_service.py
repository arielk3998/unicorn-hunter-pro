"""User management and refresh token implementation."""
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from passlib.context import CryptContext
from jose import jwt, JWTError
import secrets
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret-in-production")
REFRESH_SECRET = os.getenv("REFRESH_SECRET", "change-this-refresh-secret-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30


class UserModel(BaseModel):
    """User model for authentication."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    email: EmailStr
    username: str
    hashed_password: str
    is_active: bool = True
    created_at: Optional[datetime] = None


class TokenPair(BaseModel):
    """Access and refresh token pair."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenModel(BaseModel):
    """Refresh token storage model."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    user_id: int
    token: str
    expires_at: datetime
    revoked: bool = False
    created_at: Optional[datetime] = None


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


def create_refresh_token(user_id: int) -> tuple[str, datetime]:
    """Create refresh token and return token + expiry."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return token, expires_at


def verify_access_token(token: str) -> Optional[dict]:
    """Verify and decode access token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def create_token_pair(user_id: int, email: str) -> tuple[str, str, datetime]:
    """Create access + refresh token pair."""
    access_token = create_access_token({"sub": str(user_id), "email": email})
    refresh_token, expires_at = create_refresh_token(user_id)
    return access_token, refresh_token, expires_at
