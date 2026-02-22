from abc import abstractmethod
from typing import Optional, List

from ..entities.refresh_token import RefreshToken
from .base import BaseRepository


class IRefreshTokenRepository(BaseRepository):
    """Интерфейс репозитория refresh токенов"""

    @abstractmethod
    async def get_by_id(self, token_id: int) -> Optional[RefreshToken]:
        """Получить токен по ID"""
        pass

    @abstractmethod
    async def create(self, token: RefreshToken) -> RefreshToken:
        """Создать новый токен"""
        pass

    @abstractmethod
    async def update(self, token: RefreshToken) -> RefreshToken:
        """Обновить существующий токен"""
        pass

    @abstractmethod
    async def delete(self, token_id: int) -> bool:
        """Удалить токен"""
        pass

    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        pass

    @abstractmethod
    async def revoke(self, token_id: int) -> bool:
        """Отозвать токе"""
        pass

    @abstractmethod
    async def revoke_all_user_tokens(self, user_id: int) -> None:
        """Отозвать все токены пользователя"""
        pass

    @abstractmethod
    async def get_user_tokens(self, user_id: int) -> List[RefreshToken]:
        """Получить все токены пользователя"""
        pass