from datetime import datetime
from typing import Optional, List

from .base import DomainEntity
from typing import Optional

class Room(DomainEntity):
    def __init__(
            self,
            name: str,
            description: Optional[str],
            owner_id: int,
            is_private: bool = False,
            max_participants: int = 0,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,
            id: Optional[int] = None
    ):
        super().__init__(id)
        self.name = name
        self.description = description
        self.owner_id = owner_id
        self.is_private = is_private
        self.max_participants = max_participants
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or self.created_at
        self._participants: List[int] = []

    def add_participant(self, user_id:int):
        if user_id in self._participants:
            raise ValueError("user in room")
        if self.max_participants and len(self._participants) >= self.max_participants:
            raise ValueError("Room is full")
        self._participants.append(user_id)

    def remove_participant(self, user_id: int):
        if user_id in self._participants:
            self._participants.remove(user_id)

    @property
    def participants(self):
        return self._participants.copy()

    def __repr__(self):
        return f"Room(id={self.id}, name={self.name}, private={self.is_private})"
