from abc import abstractmethod
from typing import Optional, List

from ..entities.room import Room
from .base import BaseRepository


class IRoomRepository(BaseRepository):
    """Интерфейс репозитория комнат"""

    @abstractmethod
    async def get_by_id(self, room_id: int) -> Optional[Room]:
        """Получить комнату по ID"""
        pass

    @abstractmethod
    async def create(self, room: Room) -> Room:
        """Создать новую комнату"""
        pass

    @abstractmethod
    async def update(self, room: Room) -> Room:
        """Обновить существующую комнату"""
        pass

    @abstractmethod
    async def delete(self, room_id: int) -> bool:
        """Удалить комнату"""
        pass

    # Специфичные методы для комнат
    @abstractmethod
    async def get_user_rooms(self, user_id: int) -> List[Room]:
        """Получить все комнаты пользователя"""
        pass

    @abstractmethod
    async def add_participant(self, room_id: int, user_id: int) -> None:
        """Добавить участника в комнату"""
        pass

    @abstractmethod
    async def remove_participant(self, room_id: int, user_id: int) -> None:
        """Удалить участника из комнаты"""
        pass

    @abstractmethod
    async def get_room_participants(self, room_id: int) -> List[int]:
        """Получить список ID участников комнаты"""
        pass