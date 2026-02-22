from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
import jwt
from passlib.context import CryptContext

from chat_api.app.domain.ports.security import (
    ITokenService,
    IPasswordHasher,
    TokenPayload
)

from .config import settings
from .exceptions import InvalidTokenError


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class PasswordHasher(IPasswordHasher):
    """
    Сервис для хеширования и проверки паролей.
    """

    def hash_password(self, password: str) -> str:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def needs_rehash(self, hashed_password: str) -> bool:
        return pwd_context.needs_update(hashed_password)



class TokenService(ITokenService):


    def create_access_token(
        self,
        user_id: int,
        username: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) +timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
            "username": username
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    def create_refresh_token(
        self,
        user_id: int,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    def verify_token(self, token: str, token_type: str = "access") -> TokenPayload:
        """
        Верификация JWT токена.
        
        Args:
            token: JWT токен
            token_type: ожидаемый тип токена ("access" или "refresh")
        
        Returns:
            TokenPayload: распарсенный payload
            
        Raises:
            InvalidTokenError: если токен невалидный
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            if payload.get("type") != token_type:
                raise InvalidTokenError(f"Invalid token type. Expected {token_type}")

            if "exp" in payload:
                payload["exp"] = datetime.fromtimestamp(payload["exp"])
            
            if "iat" in payload:
                payload["iat"] = datetime.fromtimestamp(payload["iat"])

            return TokenPayload(**payload)

        except jwt.ExpiredSignatureError:
            raise InvalidTokenError("Token has expired")

        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token {str(e)}")


    def get_user_id_from_token(self, token: str) -> int:
        """
        Извлечение user_id из токена (без полной верификации).
        Использовать только для нечувствительных операций.
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False}  # Не проверяем expiration
            )
            return int(payload.get("sub"))
        except (jwt.InvalidTokenError, ValueError):
            raise InvalidTokenError("Cannot extract user_id from token")

    def create_token_pair(self, user_id: int, username: str) -> Dict[str, str]:
        """
        Создание пары access + refresh токенов.
        """
        return{
            "access_token": self.create_access_token(user_id=user_id, username=username),
            "refresh_token": self.create_refresh_token(user_id=user_id),
            "token_type": "bearer"
        }
    

def get_password_hasher() -> IPasswordHasher:
    return PasswordHasher()


def get_token_service() -> ITokenService:
    return TokenService()