import re
from typing import Optional


class Email:
    """Value Object for Email"""

    def __init__(self, value: str):
        self.value = self._normalize(value)

        if not self._is_valid(value):
            raise ValueError(f"Invalid email: {value}")

    @staticmethod
    def _normalize(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def _is_valid(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Email):
            return False
        return self.value == other.value

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Email('{self.value}')"