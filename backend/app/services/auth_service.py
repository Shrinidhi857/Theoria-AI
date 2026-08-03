import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.auth import UserSignup, UserLogin, Token
from app.schemas.user import UserRead
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)

logger = logging.getLogger(__name__)


def create_token_response(user: User) -> Token:
    """Generate access and refresh tokens for user and return Token response object."""
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    user_read = UserRead.model_validate(user)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_read
    )


def register_user(db: Session, signup_data: UserSignup) -> Token:
    """Register a new user using email & password."""
    existing_user = db.query(User).filter(User.email == signup_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )
    
    hashed_pwd = get_password_hash(signup_data.password)
    user = User(
        email=signup_data.email,
        hashed_password=hashed_pwd,
        full_name=signup_data.full_name,
        auth_provider="email",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"Registered new email user: {user.email}")
    return create_token_response(user)


def authenticate_user(db: Session, login_data: UserLogin) -> Token:
    """Authenticate email & password user."""
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    
    if not user.hashed_password or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive."
        )
    
    return create_token_response(user)


def authenticate_or_create_google_user(db: Session, google_user_info: Dict[str, Any]) -> Token:
    """
    Given validated Google User Payload:
    Check if user exists by email or google_id. If found, update google_id / avatar; if not, create new user.
    """
    email = google_user_info.get("email")
    google_id = google_user_info.get("google_id")
    full_name = google_user_info.get("full_name")
    avatar_url = google_user_info.get("avatar_url")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve email from Google login payload."
        )

    user = db.query(User).filter(
        (User.email == email) | (User.google_id == google_id)
    ).first()

    if user:
        # Update user details if needed
        if not user.google_id:
            user.google_id = google_id
        if avatar_url and not user.avatar_url:
            user.avatar_url = avatar_url
        if full_name and not user.full_name:
            user.full_name = full_name
        db.commit()
        db.refresh(user)
    else:
        # Create new Google Auth user
        user = User(
            email=email,
            full_name=full_name,
            google_id=google_id,
            avatar_url=avatar_url,
            auth_provider="google",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created new user via Google OAuth: {user.email}")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive."
        )

    return create_token_response(user)


def refresh_access_token(db: Session, refresh_token_str: str) -> Token:
    """Validate refresh token and issue new access & refresh token pair."""
    payload = decode_token(refresh_token_str)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload."
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive."
        )
    
    return create_token_response(user)
