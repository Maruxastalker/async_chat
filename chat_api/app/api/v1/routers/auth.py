from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from chat_api.app.api.dependencies import get_auth_service, get_current_user
from chat_api.app.domain.services.auth_service import AuthService
from chat_api.app.domain.entities.user import User
from chat_api.app.infrastructure.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    LogoutRequest,
    TokenResponse,
    AuthResponse,
    BaseResponse,
)
from chat_api.app.infrastructure.schemas.user import user_to_response


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
        data: RegisterRequest,
        auth_service: AuthService = Depends(get_auth_service)
):
    user, tokens = await auth_service.register(
        username=data.username,
        email=str(data.email),
        password=data.password,
    )

    return AuthResponse(
        user=user_to_response(user),
        tokens=TokenResponse(**tokens)
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
        data: RefreshTokenRequest,
        auth_service: AuthService = Depends(get_auth_service)
):
    tokens = await auth_service.refresh_token(data.refresh_token)
    return TokenResponse(**tokens)

@router.post("/login", response_model=AuthResponse)
async def login(
    data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Логин пользователя.
    """
    user, tokens = await auth_service.login(
        username=data.username,
        password=data.password,
    )

    return AuthResponse(
        user=user_to_response(user),
        tokens=TokenResponse(**tokens),
    )

@router.post("/logout", response_model=BaseResponse)
async def logout(
        data: LogoutRequest,
        auth_service: AuthService = Depends(get_auth_service),
        current_user: User = Depends(get_current_user)
):
    await auth_service.logout(user_id=current_user.id, refresh_token=data.refresh_token)
    return BaseResponse(success=True, message="Logged out")