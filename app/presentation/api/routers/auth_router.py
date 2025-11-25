"""Authentication router for login, register, refresh, and logout."""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone
from app.application.services.user_service import (
    UserModel, TokenPair, hash_password, verify_password,
    create_token_pair, verify_access_token
)
from app.infrastructure.database.sqlite_user_repo import SQLiteUserRepository
from app.infrastructure.logging.structured_logger import get_logger
import os

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = get_logger(__name__)

DB_PATH = os.getenv("DATABASE_PATH", "data/resume_toolkit.db")
user_repo = SQLiteUserRepository(DB_PATH)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    # Optional username for backward compatibility; if omitted we'll derive one
    username: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register a new user with only email & password required.
    Username becomes optional; if absent we derive one from the email local-part.
    """
    if user_repo.get_user_by_email(request.email):
        logger.warning(f"Registration attempt with existing email: {request.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    derived_username = request.username or request.email.split('@')[0]

    # Create user (keep username column for existing schema, ensure uniqueness by derivation)
    user = UserModel(
        email=request.email,
        username=derived_username,
        hashed_password=hash_password(request.password),
        is_active=True
    )
    try:
        user_id = user_repo.create_user(user)
    except Exception as e:  # uniqueness or other DB issues
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(status_code=400, detail="Could not create user (username/email may already exist)")

    access_token, refresh_token, expires_at = create_token_pair(user_id, request.email)
    user_repo.store_refresh_token(user_id, refresh_token, expires_at)
    logger.info(f"User registered successfully: {request.email}")
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenPair)
async def login(request: LoginRequest):
    """Login and return token pair."""
    user = user_repo.get_user_by_email(request.email)
    
    if not user or not verify_password(request.password, user.hashed_password):
        logger.warning(f"Failed login attempt for: {request.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {request.email}")
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    # Generate tokens
    if user.id is None:
        logger.error("User record missing ID")
        raise HTTPException(status_code=500, detail="Internal user record error")
    access_token, refresh_token, expires_at = create_token_pair(int(user.id), user.email)
    user_repo.store_refresh_token(int(user.id), refresh_token, expires_at)
    
    logger.info(f"User logged in successfully: {request.email}")
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenPair)
async def refresh(request: RefreshRequest):
    """Refresh access token using refresh token."""
    token_record = user_repo.get_refresh_token(request.refresh_token)
    
    if not token_record:
        logger.warning("Invalid refresh token used")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Check expiry
    # Use timezone-aware UTC comparison
    if token_record.expires_at < datetime.now(timezone.utc):
        logger.warning(f"Expired refresh token for user {token_record.user_id}")
        raise HTTPException(status_code=401, detail="Refresh token expired")
    
    # Get user
    user = user_repo.get_user_by_id(token_record.user_id)
    if not user or not user.is_active:
        logger.warning(f"Refresh attempt for inactive/missing user {token_record.user_id}")
        raise HTTPException(status_code=403, detail="User not found or inactive")
    
    # Revoke old token and generate new pair
    user_repo.revoke_refresh_token(request.refresh_token)
    if user.id is None:
        logger.error("User record missing ID during refresh")
        raise HTTPException(status_code=500, detail="Internal user record error")
    access_token, new_refresh_token, expires_at = create_token_pair(int(user.id), user.email)
    user_repo.store_refresh_token(int(user.id), new_refresh_token, expires_at)
    
    logger.info(f"Token refreshed for user: {user.email}")
    return TokenPair(access_token=access_token, refresh_token=new_refresh_token)


@router.post("/logout")
async def logout(request: RefreshRequest):
    """Logout by revoking refresh token."""
    token_record = user_repo.get_refresh_token(request.refresh_token)
    if token_record:
        user_repo.revoke_refresh_token(request.refresh_token)
        logger.info(f"User logged out: user_id={token_record.user_id}")
    
    return {"message": "Logged out successfully"}
