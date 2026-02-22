from abc import abstractmethod
from typing import Optional, List

from ..entities.message import Message
from .base import BaseRepository


class IMessageRepository:
    """Интерфейс репозитория сообщений"""

    @abstractmethod
    async def get_by_id(self, message_id: int) -> Optional[Message]:
        """Получить сообщение по ID"""
        pass

    @abstractmethod
    async def create(self, message: Message) -> Message:
        """Создать новое сообщение"""
        pass

    @abstractmethod
    async def delete(self, message_id: int) -> bool:
        """Удалить сообщение"""
        pass

    @abstractmethod
    async def get_room_messages(
            self,
            room_id: int,
            limit: int = 50,
            offset: int = 0,
    ) -> List[Message]:
        pass

    @abstractmethod
    async def get_last_message(self, room_id: int) -> Optional[Message]:
        pass