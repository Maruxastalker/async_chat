from fastapi import FastAPI


from contextlib import asynccontextmanager
from chat_api.app.core.db import engine
from chat_api.app.infrastructure.db.models import Base
from chat_api.app.core.redis import redis_client

from chat_api.app.api.v1.routers import auth, users, rooms, messages
from chat_api.app.api.v1.websockets import chat as ws_chat
from chat_api.app.api.v1.routers import presence

@asynccontextmanager
async def lifespan(app: FastAPI):

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        await redis_client.connect()
    except Exception as e:
        print(f"Redis connect err: {e}")


    yield

    try:
        await redis_client.disconnect()
    except Exception as e:
        print(f"Redis disconnect err: {e}")




app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(rooms.router, prefix="/api/v1")
app.include_router(messages.router, prefix="/api/v1")
app.include_router(ws_chat.router, prefix="/api/v1")
app.include_router(presence.router, prefix="/api/v1")


