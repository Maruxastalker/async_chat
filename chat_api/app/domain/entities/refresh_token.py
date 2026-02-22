from datetime import datetime
from typing import Optional
from .base import DomainEntity


class RefreshToken(DomainEntity):

    def __init__(
            self,
            user_id: int,
            token: str,
            expires_at: datetime,
            is_revoked: bool = False,
            created_at: Optional[datetime] = None,
            id: Optional[int] = None,
    ):
        super().__init__(id)
        self.user_id = user_id
        self.token = token
        self.expires_at = expires_at
        self.is_revoked = is_revoked
        self.created_at = created_at or datetime.utcnow()

    def revoke(self) -> None:
        self.is_revoked = True

    def is_expired(self, current_time: Optional[datetime] = None) -> bool:
        if current_time is None:
            current_time = datetime.utcnow()
        return current_time >= self.expires_at

    def is_valid(self, current_time: Optional[datetime] = None) -> bool:
        """
        Проверить, действителен ли токен.
        Args:
            current_time: Время для проверки (по умолчанию текущее)
        Returns:
            bool: True если токен действителен
        """
        return not self.is_revoked and not self.is_expired(current_time)

    def can_be_refreshed(self) -> bool:
        return self.is_valid()

    def __repr__(self) -> str:
        status = "revoked" if self.is_revoked else "active"
        expired = "expired" if self.is_expired() else "valid"
        return f"RefreshToken(id={self.id}, user={self.user_id}, {status}, {expired})"