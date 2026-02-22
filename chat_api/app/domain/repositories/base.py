from abc import  ABC, abstractmethod
from typing import Generic, Optional, List


class BaseRepository(ABC):
    """Базовый интерфейс репозитория для ВСЕХ репозиториев"""

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[object]:
        pass

    @abstractmethod
    async def create(self, entity: object) -> Optional[object]:
        pass

    @abstractmethod
    async def delete(self, id: int) -> Optional[object]:
        pass

    @abstractmethod
    async def update(self, entity: object) -> Optional[object]:
        pass

