# app/domain/interfaces/security.py

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from pydantic import BaseModel  # если хочешь, можно и без pydantic, но так удобнее


class TokenPayload(BaseModel):
    """
    Абстрактное представление payload’а JWT токена
    (то, что нужно домену, а не конкретному JWT).
    """
    sub: str          # subject (обычно user_id)
    exp: datetime     # expiration time
    iat: datetime     # issued at
    type: str         # "access" или "refresh"
    username: Optional[str] = None


class IPasswordHasher(ABC):
    """Интерфейс сервиса хеширования паролей."""

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Преобразовать сырой пароль в хеш."""
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверить, соответствует ли сырой пароль хешу."""
        pass

    @abstractmethod
    def needs_rehash(self, hashed_password: str) -> bool:
        """Нужно ли перехешировать пароль по новой политике."""
        pass


class ITokenService(ABC):
    """Интерфейс сервиса работы с токенами."""

    @abstractmethod
    def create_access_token(
        self,
        user_id: int,
        username: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        pass

    @abstractmethod
    def create_refresh_token(
        self,
        user_id: int,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        pass

    @abstractmethod
    def verify_token(self, token: str, token_type: str = "access") -> TokenPayload:
        """Проверка и декодирование токена. При неуспехе выбрасывает доменное/общесистемное исключение."""
        pass

    @abstractmethod
    def get_user_id_from_token(self, token: str) -> int:
        """Достать user_id из токена (можно без проверки exp)."""
        pass

    @abstractmethod
    def create_token_pair(self, user_id: int, username: str) -> Dict[str, Any]:
        """Создать пару access+refresh в виде словаря (под Pydantic-ответ)."""
        pass