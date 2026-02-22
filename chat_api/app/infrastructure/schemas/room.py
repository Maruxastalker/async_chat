from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class RoomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_private: bool = False
    max_participants: int = Field(0, ge=0)


class RoomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_private: Optional[bool] = None
    max_participants: Optional[int] = Field(None, ge=0)


class InviteUserRequest(BaseModel):
    user_id: int


class RoomResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_private: bool
    owner_id: int
    max_participants: int
    participants_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoomWithParticipants(RoomResponse):
    participants: List["UserPublic"]

class RoomListResponse(BaseModel):
    """Список комнат"""
    rooms: list[RoomResponse]
    total: int
    page: int
    per_page: int


def room_to_response(room, participants_count: int = 0) -> RoomResponse:
    """Конвертация доменного Room в Pydantic RoomResponse"""
    return RoomResponse(
        id=room.id,
        name=room.name,
        description=room.description,
        is_private=room.is_private,
        owner_id=room.owner_id,
        max_participants=room.max_participants,
        participants_count=participants_count,
        created_at=room.created_at,
        updated_at=room.updated_at if hasattr(room, 'updated_at') else room.created_at
    )

from .user import UserPublic