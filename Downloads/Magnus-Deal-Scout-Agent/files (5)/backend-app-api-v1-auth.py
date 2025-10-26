# app/api/v1/auth.py

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import Token, UserCreate, User as UserSchema, Message
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token
)
from app.api.deps import get_current_active_user
from app.config import settings

router = APIRouter()


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user account.
    
    Args:
        user_in: User registration data
        db: Database session
    
    Returns:
        Created user object
    
    Raises:
        HTTPException: If email already registered
    """
    # Check if user already exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        is_verified=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    Args:
        db: Database session
        form_data: OAuth2 form with username (email) and password
    
    Returns:
        Access token
    
    Raises:
        HTTPException: If credentials are incorrect
    """
    # Get user by email (username field in OAuth2)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserSchema)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current user object
    """
    return current_user


@router.post("/refresh", response_model=Token)
def refresh_token(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Refresh access token.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        New access token
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=current_user.id,
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/password-reset/request", response_model=Message)
def request_password_reset(
    email: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Request password reset email.
    
    Args:
        email: User email address
        db: Database session
    
    Returns:
        Success message
    
    Note:
        This is a placeholder. In production, send actual reset email.
    """
    user = db.query(User).filter(User.email == email).first()
    
    # Don't reveal if email exists for security
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/verify-email", response_model=Message)
def verify_email(
    token: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Verify user email address.
    
    Args:
        token: Email verification token
        db: Database session
    
    Returns:
        Success message
    
    Note:
        This is a placeholder. Implement actual email verification logic.
    """
    # Placeholder implementation
    return {"message": "Email verified successfully"}
