from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.schemas.user import UserRead


class UserSignup(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password (min 6 characters)")
    full_name: Optional[str] = Field(default=None, description="Full name of user")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class GoogleLoginRequest(BaseModel):
    token: str = Field(..., description="Google OAuth ID token or access token")


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    type: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str
