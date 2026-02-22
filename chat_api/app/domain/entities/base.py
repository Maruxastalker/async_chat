from abc import ABC
from datetime import datetime
from typing import Optional, Any


class DomainEntity(ABC):
    """
        Базовый класс для всех доменных сущностей.
    """

    def __init__(self, id: Optional[int] = None):
        self.id = id
        self._domain_events = []

    def add_domain_event(self, event: Any) -> None:
        self._domain_events.append(event)

    def clear_domain_event(self) -> None:
        self._domain_events.clear()

    @property
    def domain_events(self) -> list:
        return self._domain_events.copy()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DomainEntity):
            return False
        return self.id is not None and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id) if self.id else hash(id(self))