from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=8)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=8)
    email: Optional[EmailStr] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_online: bool
    is_active: bool
    last_seen: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserPublic(BaseModel):
    """Публичные данные пользователя (для списков)"""
    id: int
    username: str
    is_online: bool

class UserListResponse(BaseModel):
    users: list[UserPublic]
    total: int


def user_to_response(user) -> UserResponse:
    """Конвертация доменного User в Pydantic UserResponse"""
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_online=user.is_online,
        is_active=user.is_active,
        last_seen=user.last_seen,
        created_at=user.created_at
    )