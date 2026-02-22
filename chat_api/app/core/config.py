from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./chat_api_db/chat.db"
    DB_ECHO: bool = False

    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_TIMEOUT: int = 5

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    WS_MAX_CONNECTIONS: int = 1000
    WS_PING_INTERVAL: int = 20

    DEBUG: bool = True
    TESTING: bool = False

    class Config:
        env_file = ".env"

settings = Settings()