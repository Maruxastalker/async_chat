from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    room_id: int
    message_type: str = Field("text", pattern="^(text|image|file|system)$")
    reply_to_id: Optional[int] = None


class MessageResponse(BaseModel):
    """Ответ с данными сообщения"""
    id: int
    content: str
    room_id: int
    user_id: int
    username: str
    message_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageWithReplies(MessageResponse):
    """Сообщение с ответами"""
    replies: List["MessageResponse"]


class MessageListResponse(BaseModel):
    """Список сообщений"""
    messages: list[MessageResponse]
    total: int
    page: int
    per_page: int
    has_more: bool


def message_to_response(message, username: str = None) -> MessageResponse:
    """Конвертация доменного Message в Pydantic MessageResponse"""
    return MessageResponse(
        id=message.id,
        content=message.content,
        room_id=message.room_id,
        user_id=message.user_id,
        username=username or f"user_{message.user_id}",
        message_type=message.message_type,
        created_at=message.created_at
    )