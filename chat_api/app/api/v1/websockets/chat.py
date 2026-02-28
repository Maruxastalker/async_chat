from typing import Any, Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query

from chat_api.app.core.exceptions import InvalidTokenError
from chat_api.app.domain.ports.security import ITokenService
from chat_api.app.domain.repositories.user_repository import IUserRepository
from chat_api.app.domain.repositories.room_repository import IRoomRepository
from chat_api.app.domain.services.chat_service import ChatService
from chat_api.app.infrastructure.schemas.message import message_to_response
from chat_api.app.api.dependencies import (
    get_user_repo,
    get_room_repo,
    get_chat_service,
)
from chat_api.app.core.security import get_token_service
from chat_api.app.core.redis import RedisClient, get_redis
from chat_api.app.infrastructure.external.websocket_manager import (
    WebSocketManager,
    get_ws_manager,
)

router = APIRouter()

@router.websocket("/ws/{room_id}")
async def websocket_chat(
        websocket: WebSocket,
        room_id: int,
        token: str = Query(...),
        ws_manager: WebSocketManager = Depends(get_ws_manager),
        token_service: ITokenService = Depends(get_token_service),
        user_repo: IUserRepository = Depends(get_user_repo),
        room_repo: IRoomRepository = Depends(get_room_repo),
        chat_service: ChatService = Depends(get_chat_service),
        redis: RedisClient = Depends(get_redis),
):
    """
        WebSocket-чат для комнаты.
        1) Аутентифицирует пользователя по access-токен.
        2) Проверяет, что пользователь состоит в комнате.
        3) Принимает JSON от клиента, вызывает ChatService.send_message,
           и рассылает сообщение всем участникам комнаты.
    """

    try:
        payload = token_service.verify_token(token, token_type="access")
        user_id = int(payload.sub)
    except (InvalidTokenError, ValueError, TypeError):
        await websocket.close(code=1008)
        return

    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        await websocket.close(code=1008)
        return
    participants = await room_repo.get_room_participants(room_id)
    if user_id not in participants:
        await websocket.close(code=1008)

    await ws_manager.connect(room_id, websocket)

    connection_id = str(id(websocket))

    try:
        await redis.set_online_status(user_id, True)
        await redis.update_user_activity(user_id)

        await redis.add_user_to_room(room_id, user_id)

        await redis.set_ws_connections(int(connection_id), user_id, room_id)

    except Exception as e:
        print(f"Redis error on connect: {e}")

    try:
        while True:
            data: Dict[str, Any] = await websocket.receive_json()

            action = data.get("action")

            if action == "ping":
                await websocket.send_json({"event": "pong"})
                continue

            if action == "send_message":
                content = data.get("content")
                message_type = data.get("message_type", "text")
                reply_to_id = data.get("reply_to_id")

                if not content:
                    await websocket.send_json(
                        {
                            "event": "error",
                            "message": "content is required"
                        }
                    )
                    continue

                try:
                    await redis.update_user_activity(user_id)
                    await redis.increment_message_counter(room_id)
                except Exception as e:
                    print(f"Redis error on message: {e}")


                msg = await chat_service.send_message(
                    content=content,
                    room_id=room_id,
                    user_id=user_id,
                    message_type=message_type,
                    reply_to_id=reply_to_id,
                )

                msg_resp = message_to_response(msg, username=user.username)

                await ws_manager.broadcast(
                    room_id,
                    {
                        "event": "message",
                        "message": msg_resp.model_dump(),
                    },
                )

            else:
                await websocket.send_json(
                    {
                        "event": "error",
                        "message": f"Unknown action: {action}",
                    }
                )
    except WebSocketDisconnect:
        await ws_manager.disconnect(room_id, websocket)

    except Exception:
        await ws_manager.disconnect(room_id, websocket)
        await websocket.close(code=1011)

    finally:
        try:

            await redis.remove_ws_connection(connection_id)

            await redis.remove_user_from_room(room_id, user_id)

            remaining = await redis.get_user_ws_connections(user_id)

            if not remaining:
                await redis.set_online_status(user_id, False)

        except Exception as e:
            print(f"Redis error on disconnect: {e}")
