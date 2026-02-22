from fastapi import APIRouter, Depends

from chat_api.app.core.redis import RedisClient, get_redis

router = APIRouter(prefix="/presence", tags=["presence"])

@router.get("/online/users")
async def get_online_users(
        redis: RedisClient = Depends(get_redis)
):
    """
        Получить список онлайн-пользователей по данным Redis.
    """

    user_ids = await redis.get_online_users()

    return {
        "online_users_ids": user_ids,
        "total": len(user_ids)
    }

@router.get("/rooms/{room_id}/users")
async def get_room_active_chat(
        room_id: int,
        redis: RedisClient = Depends(get_redis)
):
    """
        Получить список активных пользователей в комнате (есть активное WS-соединение).
    """

    user_ids = await redis.get_room_active_users(room_id)

    return {
        "room_id": room_id,
        "active_user_ids": user_ids,
        "total": len(user_ids),
    }
