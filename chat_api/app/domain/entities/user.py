from datetime import datetime
from typing import Optional

from .base import DomainEntity


class User(DomainEntity):
    def __init__(
            self,
            username: str,
            email: str,
            hashed_password: str,
            is_active: bool = True,
            is_online: bool = False,
            last_seen: Optional[datetime] = None,
            created_at: Optional[datetime] = None,
            id: Optional[int] = None
    ):
        super().__init__(id)
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.is_online = is_online
        self.last_seen = last_seen
        self.created_at = created_at or datetime.utcnow()

    def change_password(self, new_hash: str):
        self.hashed_password = new_hash

    def set_online(self):
        self.is_online = True
        self.last_seen = datetime.utcnow()

    def set_offline(self):
        self.is_online = False
        self.last_seen = datetime.utcnow()

    def __repr__(self):
        return f"User(id={self.id}, username={self.username})"