from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from .config import settings


class DomainException(Exception):
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class InvalidTokenError(DomainException):

    def __init__(
        self,
        message: str = "Invalid or expired token"
    ):
        super().__init__(
            message=message,
            errod_code="INVALID_TOKEN",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class RedisConnectionError(DomainException):
    """Ошибка подключения к Redis."""
    
    def __init__(self, message: str = "Redis connection error"):
        super().__init__(
            message=message,
            error_code="REDIS_CONNECTION_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


class UserAlreadyExists(DomainException):
    def __init__(self, username: str, email: str):
        super().__init__(
            message=f"User with username '{username}' or email '{email}' already exists",
            errod_code="USER_ALREADY_EXISTS",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"username": username, "email": email}
        )


class UserNotFound(DomainException):
    """Пользователь не найден."""
    
    def __init__(self, user_id: Optional[int] = None, username: Optional[str] = None):
        identifier = f"ID {user_id}" if user_id else f"username '{username}'"
        super().__init__(
            message=f"User with {identifier} not found",
            error_code="USER_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"user_id": user_id, "username": username}
        )


class InvalidCredentials(DomainException):
    """Неверные учетные данные."""

    def __init__(self):
        super().__init__(
            message="Invalid username or password",
            error_code="INVALID_CREDENTIALS",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class RoomNotFound(DomainException):

    def __init__(self, room_id: int):
        super().__init__(
            message=f"Room wit ID {room_id} not found",
            errod_code="ROOM_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"room_id": room_id}
        )


class NotRoomMember(DomainException):
    """Пользователь не является участником комнаты."""

    def __init__(self, user_id: int, room_id: int):
        super().__init__(
            message=f"User {user_id} is not a member of room {room_id}",
            error_code="NOT_ROOM_MEMBER",
            status_code=status.HTTP_403_FORBIDDEN,
            details={"user_id": user_id, "room_id": room_id}
        )


class ForbiddenAction(DomainException):
    """Запрещенное действие"""

    def __init__(self, action: str, reason: str =""):
        message = f"Forbidden to {action}"
        if reason:
            message += f": {reason}"
        super().__init__(
            message=message,
            errod_code="FORBIDDEN_ACTION",
            status_code=status.HTTP_403_FORBIDDEN,
            details={"action": action, "reason": reason}
        )


class MessageNotFound(DomainException):
    """Сообщение не найдено."""
    
    def __init__(self, message_id: int):
        super().__init__(
            message=f"Message with ID {message_id} not found",
            error_code="MESSAGE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"message_id": message_id}
        )


class RedisConnectionError(DomainException):

    def __init__(self, message: str = "Redis connection error"):
        super().__init__(
            message=message,
            errod_code="REDIS_CONNECTION_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class ValidationError(DomainException):
    """Ошибка валидации данных."""
    
    def __init__(self, field: str, error: str):
        super().__init__(
            message=f"Validation error for field '{field}': {error}",
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"field": field, "error": error}
        )


def setup_exception_handlers(app):
    """
    Настройка обработчиков исключений для FastAPI приложения.
    Вызывается в main.py.
    """

    @app.exception_handler(DomainException)
    async def handle_domain_exception(request, exc: DomainException):
        """
        Обработчик доменных исключений.
        Преобразует DomainException в HTTPException с нужным форматом.
        """

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request, exc: HTTPException):
        """
        Обработчик стандартных HTTP исключений.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_ERROR",
                    "message": exc.detail,
                    "details": {}
                }
            }
        )

    @app.exception_handler(Exception)
    async def handle_general_exception(request, exc: Exception):
        """
        Обработчик всех непредвиденных исключений.
        В продакшене здесь нужно добавить логирование.
        """
        # В режиме разработки показываем traceback
        if settings.DEBUG:
            raise exc
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Internal server error",
                    "details": {}
                }
            }
        )