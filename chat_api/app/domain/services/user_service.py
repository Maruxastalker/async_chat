from ..entities.user import User
from chat_api.app.core.exceptions import UserNotFound, InvalidCredentials
from ..repositories.user_repository import IUserRepository
from ..ports.security import IPasswordHasher


class UserService:
    """
    Сервис работы с пользователями.
    """

    def __init__(
            self,
            user_repo: IUserRepository,
            password_hasher: IPasswordHasher,
    ):
        self.user_repo = user_repo
        self.password_hasher = password_hasher

    async def get_user(self, user_id: int) -> User:
        """
                Получить пользователя по ID.

                Args:
                    user_id: ID пользователя

                Returns:
                    User: Доменная сущность пользователя

                Raises:
                    UserNotFound: Если пользователь не найден
        """

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound()

        return user

    async def update_profile(self, user_id: int, new_username: str) -> User:
        """
                Обновить профиль пользователя.

                Args:
                    user_id: ID пользователя
                    new_username: Новое имя пользователя (опционально)

                Returns:
                    User: Обновлённый пользователь

                Raises:
                    UserNotFound: Если пользователь не найден
                    ValueError: Если username уже занят
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound(user_id=user_id)

        if new_username is not None:
            existing = await self.user_repo.get_by_username(new_username)
            if existing and existing.id != user_id:
                raise ValueError(f"Username '{new_username}' already taken")
            user.username = new_username

        return await self.user_repo.update(user)


    async def change_password(self, user_id, current_password: str, new_password: str) -> None:
        """
                Смена пароля.

                Args:
                    user_id: ID пользователя
                    current_password: Текущий пароль
                    new_password: Новый пароль

                Raises:
                    UserNotFound: Если пользователь не найден
                    InvalidCredentials: Если текущий пароль неверный
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound(user_id)

        if not self.password_hasher.verify_password(current_password, user.hashed_password):
            raise InvalidCredentials()

        new_hash = self.password_hasher.hash_password(new_password)
        user.change_password(new_hash)
        await self.user_repo.update(user)

    async def set_online_status(self, user_id: int, is_online: bool) -> User:
        """
                Установить статус онлайн/оффлайн.

                Args:
                    user_id: ID пользователя
                    is_online: True для онлайн, False для оффлайн

                Returns:
                    User: Обновлённый пользователь
        """

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound(user_id)

        if is_online:
            user.set_online()
        else:
            user.set_offline()

        return await self.user_repo.update(user)