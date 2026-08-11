import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import (
    UserSignup, UserLogin, GoogleLoginRequest, Token, RefreshTokenRequest
)
from app.core.google_auth import verify_google_user_from_token_or_auth_code
from app.services.auth_service import (
    register_user,
    authenticate_user,
    authenticate_or_create_google_user,
    refresh_access_token
)

try:
    from app.core.logging_config import setup_colored_logging
    logger = setup_colored_logging(__name__)
except ImportError:
    logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(
    signup_data: UserSignup,
    db: Session = Depends(get_db)
):
    """
    Register a new user account with Email and Password.
    Returns access token, refresh token, and user profile metadata.
    """
    return register_user(db=db, signup_data=signup_data)


@router.post("/login", response_model=Token)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user via Email and Password (JSON body).
    Returns access token, refresh token, and user profile metadata.
    """
    return authenticate_user(db=db, login_data=login_data)


@router.post("/google", response_model=Token)
async def google_auth(
    google_req: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user using Google OAuth ID Token or Google Access Token.
    If user account does not exist, automatically registers user.
    """
    google_user_info = await verify_google_user_from_token_or_auth_code(google_req.token)
    if not google_user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or unverified Google token."
        )

    return authenticate_or_create_google_user(db=db, google_user_info=google_user_info)


@router.post("/refresh", response_model=Token)
def refresh(
    req: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Exchange valid refresh token for fresh access token and refresh token.
    """
    return refresh_access_token(db=db, refresh_token_str=req.refresh_token)
