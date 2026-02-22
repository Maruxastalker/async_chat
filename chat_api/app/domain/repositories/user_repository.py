from abc import abstractmethod
from typing import Optional, List

from ..entities.user import User
from .base import BaseRepository


class IUserRepository(BaseRepository):
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Найти пользователя по username"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Найти пользователя по email"""
        pass

    @abstractmethod
    async def search_users(self, query: str, limit: int = 10) -> List[User]:
        """Поиск пользователей по имени"""
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        """Создать нового пользователя"""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Обновить существующего пользователя"""
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Удалить пользователя"""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        pass