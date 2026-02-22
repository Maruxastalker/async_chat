import asyncio
from typing import Dict, Set

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class WebSocketManager:
    """
        Простой in-memory менеджер WebSocket-подключений.
        Хранит подключения по room_id.
    """

    def __init__(self) -> None:
        self._connections: Dict[int, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, room_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            if room_id not in self._connections:
                self._connections[room_id] = set()
            self._connections[room_id].add(websocket)

    async def disconnect(self, room_id: int, websocket: WebSocket) -> None:

        async with self._lock:
            conns = self._connections.get(room_id)
            if conns and websocket in conns:
                conns.remove(websocket)
                if not conns:
                    del self._connections[room_id]

    async def broadcast(self, room_id: int, message) -> None:
        async with self._lock:
            conns = list(self._connections.get(room_id, set()))

        for ws in conns:
            try:
                if isinstance(message, str):
                    await ws.send_text(message)
                else:
                    await ws.send_json(message)
            except WebSocketDisconnect:
                await self.disconnect(room_id, ws)


ws_manager = WebSocketManager()

def get_ws_manager() -> WebSocketManager:
    return ws_manager