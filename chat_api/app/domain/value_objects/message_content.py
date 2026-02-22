from typing import Optional

class MessageContent:
    """Value Object для содержимого сообщения"""

    MAX_LENGTH = 200

    def __init__(self, value: str):
        self.value = value.strip()

        if not self.value:
            raise ValueError("Message content cannot be empty")

        if len(self.value) > self.MAX_LENGTH:
            raise ValueError(f"Message too long. Max {self.MAX_LENGTH} characters")

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        preview = self.value[:20] + "..." if len(self.value) > 20 else self.value
        return f"MessageContent('{preview}')"