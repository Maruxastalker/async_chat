from typing import List

from fastapi import APIRouter, Depends, status

from chat_api.app.api.dependencies import (
    get_current_user,
    get_room_service,
    get_room_repo,
)
from chat_api.app.domain.entities.user import User
from chat_api.app.domain.services.room_service import RoomService
from chat_api.app.domain.repositories.room_repository import IRoomRepository
from chat_api.app.infrastructure.schemas.room import (
    RoomCreate,
    RoomUpdate,
    InviteUserRequest,
    RoomResponse,
    RoomListResponse,
    room_to_response,
)
from chat_api.app.infrastructure.schemas.auth import BaseResponse

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    data: RoomCreate,
    current_user: User = Depends(get_current_user),
    room_service: RoomService = Depends(get_room_service),
    room_repo: IRoomRepository = Depends(get_room_repo),
):
    """
    Создать новую комнату.
    """
    room = await room_service.create_room(
        name=data.name,
        owner_id=current_user.id,
        description=data.description,
        is_private=data.is_private,
        max_participants=data.max_participants,
    )

    # Создатель – единственный участник по умолчанию
    participants = await room_repo.get_room_participants(room.id)
    return room_to_response(room, participants_count=len(participants))

@router.get("/my", response_model=RoomListResponse)
async def get_my_rooms(
    current_user: User = Depends(get_current_user),
    room_service: RoomService = Depends(get_room_service),
    room_repo: IRoomRepository = Depends(get_room_repo),
):
    rooms = await room_service.get_user_rooms(current_user.id)

    room_responses: List[RoomResponse] = []

    for room in rooms:
        participants = await room_repo.get_room_participants(room.id)
        room_responses.append(
            room_to_response(room, participants_count=len(participants))
        )

    return RoomListResponse(
        rooms=room_responses,
        total=len(room_responses),
        page=1,
        per_page=len(room_responses)
    )

@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    room_service: RoomService = Depends(get_room_service),
    room_repo: IRoomRepository = Depends(get_room_repo),
):
    """
    Информация о комнате.
    """
    room = await room_service.get_room(room_id)
    participants = await room_repo.get_room_participants(room.id)
    return room_to_response(room, participants_count=len(participants))

@router.post("/{room_id}/invite", response_model=BaseResponse)
async def invite_user(
    room_id: int,
    data: InviteUserRequest,
    current_user: User = Depends(get_current_user),
    room_service: RoomService = Depends(get_room_service),
):
    await room_service.add_user_to_room(
        room_id=room_id,
        user_id=data.user_id,
        inviter_id=current_user.id,
    )

    return BaseResponse(success=True, message="User invited in room")

@router.post("/{room_id}/leave", response_model=BaseResponse)
async def leave_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    room_service: RoomService = Depends(get_room_service),
):
    await room_service.remove_user_from_room(
        room_id=room_id,
        user_id=current_user.id,
        remover_id=current_user.id,
    )

    return BaseResponse(success=True, message="Left room")

