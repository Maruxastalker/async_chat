from fastapi import Depends, HTTPException, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from chat_api.app.core.db import get_db_session
from chat_api.app.core.security import get_password_hasher, get_token_service
from chat_api.app.core.exceptions import InvalidTokenError

from chat_api.app.domain.entities.user import User
from chat_api.app.domain.ports.security import IPasswordHasher, ITokenService
from chat_api.app.domain.repositories.user_repository import IUserRepository
from chat_api.app.domain.repositories.room_repository import IRoomRepository
from chat_api.app.domain.repositories.message_repository import IMessageRepository
from chat_api.app.domain.repositories.refresh_token_repository import IRefreshTokenRepository
from chat_api.app.domain.services.auth_service import AuthService
from chat_api.app.domain.services.user_service import UserService
from chat_api.app.domain.services.room_service import RoomService
from chat_api.app.domain.services.chat_service import ChatService

from chat_api.app.infrastructure.db.repositories.user_repo import UserRepository
from chat_api.app.infrastructure.db.repositories.room_repo import RoomRepository
from chat_api.app.infrastructure.db.repositories.message_repo import MessageRepository
from chat_api.app.infrastructure.db.repositories.refresh_token_repo import RefreshTokenRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_user_repo(
        db: AsyncSession = Depends(get_db_session)
) -> IUserRepository:
    return UserRepository(db)

async def get_room_repo(
        db: AsyncSession = Depends(get_db_session)
) -> IRoomRepository:
    return RoomRepository(db)

async def get_message_repo(
        db: AsyncSession = Depends(get_db_session)
) -> IMessageRepository:
    return MessageRepository(db)

async def get_refresh_token_repo(
    db: AsyncSession = Depends(get_db_session),
) -> IRefreshTokenRepository:
    return RefreshTokenRepository(db)


def get_auth_service(
        user_repo: IUserRepository = Depends(get_user_repo),
        token_repo: IRefreshTokenRepository = Depends(get_refresh_token_repo),
        password_hasher: IPasswordHasher = Depends(get_password_hasher),
        token_service: ITokenService = Depends(get_token_service),
) -> AuthService:
    return AuthService(
        user_repo=user_repo,
        token_repo=token_repo,
        password_hasher=password_hasher,
        token_service=token_service,
    )

def get_user_service(
        user_repo: IUserRepository = Depends(get_user_repo),
        password_hasher: IPasswordHasher = Depends(get_password_hasher)
)-> UserService:
    return UserService(
        user_repo=user_repo,
        password_hasher=password_hasher
    )

def get_room_service(
    room_repo: IRoomRepository = Depends(get_room_repo),
    user_repo: IUserRepository = Depends(get_user_repo),
) -> RoomService:
    return RoomService(
        room_repo=room_repo,
        user_repo=user_repo,
    )

def get_chat_service(
        message_repo: IMessageRepository = Depends(get_message_repo),
        room_repo: IRoomRepository = Depends(get_room_repo),
) -> ChatService:
    return ChatService(
        message_repo=message_repo,
        room_repo=room_repo,
    )

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        token_service: ITokenService = Depends(get_token_service),
        user_repo: IUserRepository = Depends(get_user_repo),
) -> User:
    """
        Получить текущего аутентифицированного пользователя по access-токену.
    """

    try:
        payload = token_service.verify_token(token, token_type="access")
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
     user_id = int(payload.sub)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
