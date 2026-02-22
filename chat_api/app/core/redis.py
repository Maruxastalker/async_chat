from typing import Optional, AsyncGenerator

import redis.asyncio as redis
from redis.asyncio import Redis
from redis.exceptions import RedisError
import time

from .config import settings
from .exceptions import RedisConnectionError


class RedisClient:
    """
    Асинхронный клиент Redis с подключением и базовыми операциями.
    Используется для:
    - Онлайн-статусов пользователей
    - Кэширования
    - Хранения активных WebSocket соединений
    - Rate limiting
    """

    def __init__(self):
        self._redis: Optional[Redis] = None
        self._is_connected = False

    async def connect(self) -> None:
        """
        Установка соединения с Redis.
        Вызывать при старте приложения.
        """
        try:
            self._redis = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_keepalive=True,
                retry_on_timeout=True,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
            )

            await self._redis.ping()
            self._is_connected=True

        except (RedisError, ConnectionError) as e:
            self._is_connected = False
            raise RedisConnectionError(f"Failed to connect to Redis: {str(e)}")

    async def disconnect(self) -> None:
        """
        Закрытие соединения с Redis.
        Вызывать при остановке приложения.
        """
        if self._redis and self._is_connected:
            await self._redis.close()
            self._is_connected=False
            self._redis=None

    @property
    def client(self) -> Redis:
        """
        Получение Redis клиента.
        Проверяет, что соединение установлено.
        """
        if not self._redis or not self._is_connected:
            raise RedisConnectionError("Redis client is not connected")
        return self._redis

    async def is_connected(self) -> bool:
        """
        Проверка активности соединения.
        """
        if not self._redis:
            return False

        try:
            await self._redis.ping()
            return True
        except RedisError:
            return False

    async def set_online_status(self, user_id: int, is_online: bool = True) -> None:
        """
        Установить онлайн-статус пользователя.
        
        Храним в Redis Set: online_users -> {user_id1, user_id2, ...}
        Если offline - удаляем из Set.
        """
        key = "online_users"

        if is_online:
            await self.client.sadd(key, str(user_id))
            await self.client.expire(key, 300)
        else:
            await self.client.srem(key, str(user_id))

    async def get_online_users(self) -> list[int]:
        """
        Получить список ID онлайн-пользователей.
        """
        key = "online_users"
        members = await self.client.smembers(key)
        return [int(user_id) for user_id in members if user_id.isdigit()]

    async def is_user_online(self, user_id: int) -> bool:
        """
        Проверка, онлайн ли пользователь.
        """
        key = "online_users"
        return await self.client.sismember(key, str(user_id))

    async def update_user_activity(self, user_id: int) -> None:
        """
        Обновить время последней активности пользователя.
        Используется для определения 'был в сети недавно'.
        
        Храним в Hash: user_activity:{user_id} -> timestamp
        """
        key = f"user_activity:{user_id}"
        await self.client.hset(key, "last_seen", str(int(time.time())))
        await self.client.expire(key, 86400)

    async def get_user_last_seen(self, user_id: int) -> Optional[int]:
        """
        Получить timestamp последней активности пользователя.
        """
        key = f"user_activity:{user_id}"
        last_seen = await self.client.hget(key, "last_seen")
        return int(last_seen) if last_seen else None
    
    async def add_user_to_room(self, room_id: int, user_id: int) -> None:
        """
        Добавить пользователя в список активных пользователей комнаты.
        Используется для быстрого получения списка кто в комнате.
        
        Храним в Set: room:{room_id}:active_users -> {user_id1, user_id2, ...}
        """
        key = f"room:{room_id}:active_users"
        await self.client.sadd(key, str(user_id))
    
    async def remove_user_from_room(self, room_id: int, user_id: int) -> None:
        """
        Удалить пользователя из списка активных пользователей комнаты.
        """
        key = f"room:{room_id}:active_users"
        await self.client.srem(key, str(user_id))

    async def get_room_active_users(self, room_id: int) -> list[int]:
        """
        Получить список активных пользователей в комнате.
        """
        key = f"room:{room_id}:active_users"
        members = await self.client.smembers(key)
        return [int(user_id) for user_id in members if user_id.isdigit()]
    
    async def clean_room_users(self, room_id: int) -> None:
        """
        Очистить список активных пользователей комнаты.
        Полезно при очистке кэша или перезагрузке сервера.
        """
        key = f"room:{room_id}:active_users"
        await self.client.delete(key)

    async def increment_message_counter(self, room_id: int) -> int:
        """
        Инкрементировать счётчик сообщений в комнате.
        Возвращает новое значение.
        """
        key = f"room:{room_id}:message_count"
        return await self.client.incr(key)

    async def get_message_count(self, room_id: int) -> int:
        """
        Получить количество сообщений в комнате.
        """
        key = f"room:{room_id}:message_count"
        count = await self.client.get(key)
        return int(count) if count else 0
    
    async def set_ws_connections(self, connection_id: int, user_id: int, room_id: int) -> None:
        """
        Сохранить информацию о WebSocket соединении.
        
        Структура:
        - ws:connections:{connection_id} -> {"user_id": X, "room_id": Y}
        - ws:user:{user_id}:connections -> {connection_id1, connection_id2}
        - ws:room:{room_id}:connections -> {connection_id1, connection_id2}
        """
        conn_key = f"ws:connections:{connection_id}"
        await self.client.hset(conn_key, mapping={
            "user_id": user_id,
            "room_id": room_id,
            "connected_at": str(int(time.time()))
        })
        await self.client.expire(conn_key, 3600)

        # Связь пользователь -> соединения
        user_conn_key = f"ws:user:{user_id}:connections"
        await self.client.sadd(user_conn_key, connection_id)
        await self.client.expire(user_conn_key, 3600)
        
        # Связь комната -> соединения
        room_conn_key = f"ws:room:{room_id}:connections"
        await self.client.sadd(room_conn_key, connection_id)
        await self.client.expire(room_conn_key, 3600)
    
    async def remove_ws_connection(self, connection_id: str) -> Optional[dict]:
        """
        Удалить информацию о WebSocket соединении.
        Возвращает данные о соединении, если они были.
        """
        conn_key = f"ws:connections:{connection_id}"
        conn_data = await self.client.hgetall(conn_key)

        if not conn_data:
            return None

        user_id = conn_data.get("user_id")
        room_id = conn_data.get("room_id")

        await self.client.delete(conn_key)

        if user_id:
            user_conn_key = f"ws:user:{user_id}:connections"
            await self.client.srem(user_conn_key, connection_id)

        if room_id:
            room_conn_key = f"ws:room:{room_id}:connections"
            await self.client.srem(room_conn_key, connection_id)

        return conn_data

    async def get_user_ws_connections(self, user_id: int) -> list[str]:
        """
        Получить все WebSocket соединения пользователя.
        """
        key = f"ws:user:{user_id}:connections"
        return list(await self.client.smembers(key))
    
    async def get_room_ws_connections(self, room_id: int) -> list[str]:
        """
        Получить все WebSocket соединения в комнате.
        """
        key = f"ws:room:{room_id}:connections"
        return list(await self.client.smembers(key))

    
redis_client = RedisClient()

async def get_redis() -> RedisClient:
    """
    Получить Redis клиент для dependency injection.
    Проверяет соединение при каждом запросе.
    """
    if not await redis_client.is_connected():
        await redis_client.connect()
    return redis_client