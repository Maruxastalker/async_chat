from typing import List

from fastapi import APIRouter, Depends, Query, status

from chat_api.app.api.dependencies import (
    get_current_user,
    get_chat_service,
)
from chat_api.app.domain.entities.user import User
from chat_api.app.domain.services.chat_service import ChatService
from chat_api.app.infrastructure.schemas.message import (
    MessageCreate,
    MessageResponse,
    MessageListResponse,
    message_to_response,
)
from chat_api.app.infrastructure.schemas.auth import BaseResponse


router = APIRouter(prefix="/rooms", tags=["messages"])

@router.get("/{room_id}/messages", response_model=MessageListResponse)
async def get_room_messages(
        room_id: int,
        current_user: User = Depends(get_current_user),
        chat_service: ChatService = Depends(get_chat_service),
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0)
):
    messages = await chat_service.get_room_messages(
        room_id=room_id,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )

    responses: List[MessageResponse] = [
        message_to_response(m) for m in messages
    ]
    total = len(responses)

    return MessageListResponse(
        messages=responses,
        total=total,
        page=offset // limit +1,
        per_page=limit,
        has_more=total == limit
    )

@router.post("/{room_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message_http(
    room_id: int,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Отправить сообщение через HTTP (удобно для тестов).
    В боевом чате основная отправка будет по WebSocket.
    """

    message = await chat_service.send_message(
        content=data.content,
        room_id=room_id,
        user_id=current_user.id,
        message_type=data.message_type,
        reply_to_id=data.reply_to_id,
    )

    return message_to_response(message)