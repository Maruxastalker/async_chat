from typing import Tuple, Dict

from ..entities.user import User
from ..entities.refresh_token import RefreshToken
from chat_api.app.core.exceptions import InvalidCredentials, UserAlreadyExists
from ..repositories.user_repository import IUserRepository
from ..repositories.refresh_token_repository import IRefreshTokenRepository
from chat_api.app.domain.value_objects.email import Email
from ..ports.security import ITokenService, IPasswordHasher

class AuthService:
    """
        Сервис аутентификации.
        Работает только с простыми типами Python и доменными сущностями.
    """

    def __init__(
            self,
            user_repo: IUserRepository,
            token_repo: IRefreshTokenRepository,
            password_hasher: IPasswordHasher,
            token_service: ITokenService,
    ):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.password_hasher = password_hasher
        self.token_service = token_service

    async def register(
            self,
            username: str,
            email: str,
            password: str
    ) -> Tuple[User, Dict[str, str]]:
        """
                Регистрация нового пользователя.
                Args:
                    username: Имя пользователя
                    email: Email
                    password: Пароль
                Returns:
                    Tuple[User, Dict]: Пользователь и токены
                Raises:
                    UserAlreadyExists: Если пользователь уже существует
        """

        existing_user = await self.user_repo.get_by_username(username)
        existing_email = await self.user_repo.get_by_email(email)

        if existing_user or existing_email:
            raise UserAlreadyExists(username=username, email=email)

        hashed_password = self.password_hasher.hash_password(password)

        email_vo = Email(email)

        user = User(
            username=username,
            email=str(email_vo),
            hashed_password=hashed_password
        )

        saved_user = await self.user_repo.create(user)

        tokens = self.token_service.create_token_pair(
            user_id=saved_user.id,
            username=saved_user.username
        )

        refresh_token_str = tokens["refresh_token"]
        payload = self.token_service.verify_token(
            refresh_token_str, token_type="refresh"
        )
        refresh_entity = RefreshToken(
            user_id=saved_user.id,
            token=refresh_token_str,
            expires_at=payload.exp,
        )
        await self.token_repo.create(refresh_entity)

        return saved_user, tokens

    async def login(self, username: str, password: str) -> Tuple[User, Dict[str, str]]:
        """
                Вход пользователя.

                Args:
                    username: Имя пользователя
                    password: Пароль

                Returns:
                    Tuple[User, Dict]: Пользователь и токены

                Raises:
                    InvalidCredentials: Если данные неверные
        """
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise InvalidCredentials()

        if not self.password_hasher.verify_password(password, user.hashed_password):
            raise InvalidCredentials()

        if not user.is_active:
            raise InvalidCredentials()

        user.set_online()
        await self.user_repo.update(user)

        tokens = self.token_service.create_token_pair(
            user_id=user.id,
            username=user.username
        )

        refresh_token_str = tokens["refresh_token"]
        payload = self.token_service.verify_token(
            refresh_token_str, token_type="refresh"
        )
        refresh_entity = RefreshToken(
            user_id=user.id,
            token=refresh_token_str,
            expires_at=payload.exp,
        )

        await self.token_repo.create(refresh_entity)

        return user, tokens


    async def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
                Обновление токенов.

                Args:
                    refresh_token: Refresh токен

                Returns:
                    Dict: Новые токены

                Raises:
                    InvalidCredentials: Если токен невалидный
        """
        payload = self.token_service.verify_token(refresh_token, "refresh")
        user_id = int(payload.sub)

        token_entity = await self.token_repo.get_by_token(refresh_token)
        if not token_entity and token_entity.is_valid():
            raise InvalidCredentials()

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise InvalidCredentials()

        return self.token_service.create_token_pair(
            user_id=user.id,
            username=user.username
        )

    async def logout(self, user_id: int, refresh_token: str) -> None:
        """
                Выход пользователя.

                Args:
                    user_id: ID пользователя
                    refresh_token: Refresh токен для отзыва
        """
        user = await self.user_repo.get_by_id(user_id)
        if user:
            user.set_offline()
            await self.user_repo.update(user)

        token_entity = await self.token_repo.get_by_token(refresh_token)
        if token_entity:
            await self.token_repo.revoke(token_entity.id)

