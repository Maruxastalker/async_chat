from fastapi import APIRouter, Depends, status

from chat_api.app.api.dependencies import get_current_user, get_user_service
from chat_api.app.domain.entities.user import User
from chat_api.app.domain.services.user_service import UserService
from chat_api.app.infrastructure.schemas.user import (
    UserResponse,
    UserUpdate,
    ChangePasswordRequest,
    user_to_response,
)
from chat_api.app.infrastructure.schemas.auth import BaseResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def get_me(
        current_user: User = Depends(get_current_user)
):
    return user_to_response(current_user)

@router.patch("/me", response_model=UserResponse)
async def update_me(
        data: UserUpdate,
        current_user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
):
    updated = await user_service.update_profile(
        user_id = current_user.id,
        new_username=data.username,
    )
    return user_to_response(updated)

@router.post("/me/change-password", response_model=BaseResponse)
async def change_password(
        data: ChangePasswordRequest,
        current_user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
):
    await user_service.change_password(
        user_id=current_user.id,
        current_password=data.current_password,
        new_password=data.new_password,
    )
    return BaseResponse(success=True, message="Password changed successfully")