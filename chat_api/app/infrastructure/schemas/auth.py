from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=8)
    password: str = Field(..., min_length=8, max_length=50)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=8)
    email: EmailStr
    password: str = Field(..., min_length=8)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None


class AuthResponse(BaseModel):
    user: "UserResponse"
    tokens: TokenResponse


class BaseResponse(BaseModel):
    """Базовый ответ с мета-информацией"""
    success: bool = True
    message: Optional[str] = None


from .user import UserResponse