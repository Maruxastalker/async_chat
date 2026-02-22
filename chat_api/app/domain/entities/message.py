from datetime import datetime
from typing import Optional
from .base import DomainEntity


class Message(DomainEntity):
    def __init__(
            self,
            content: str,
            room_id: int,
            user_id: int,
            message_type: str = "text",
            reply_to_id: Optional[int] = None,
            created_at: Optional[datetime] = None,
            id: Optional[int] = None
    ):
        super().__init__(id)
        self.content = content
        self.room_id = room_id
        self.user_id = user_id
        self.message_type = message_type
        self.reply_to_id = reply_to_id
        self.created_at = created_at or datetime.utcnow()

    def __repr__(self):
        return f"Message(id={self.id}, user={self.user_id}, room={self.room_id})"

