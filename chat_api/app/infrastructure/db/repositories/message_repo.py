from typing import Optional, List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from chat_api.app.domain.entities.message import Message
from chat_api.app.domain.repositories.message_repository import IMessageRepository
from chat_api.app.infrastructure.db.models import MessageModel


class MessageRepository(IMessageRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain(model: MessageModel) -> Message:
        return Message(
            id=model.id,
            content=model.content,
            room_id=model.room_id,
            user_id=model.user_id,
            message_type=model.message_type,
            reply_to_id=model.reply_to_id,
            created_at=model.created_at,
        )

    async def get_by_id(self, message_id: int) -> Optional[Message]:
        model = await self.session.get(MessageModel, message_id)
        if not model:
            return None

        return self._to_domain(model)

    async def create(self, message: Message) -> Message:
        model = MessageModel(
            content=message.content,
            room_id=message.room_id,
            user_id=message.user_id,
            message_type=message.message_type,
            reply_to_id=message.reply_to_id,
        )

        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def delete(self, message_id: int) -> bool:
        model = await self.session.get(MessageModel, message_id)
        if not model:
            return False
        else:
            await self.session.delete(model)
            return True

    async def get_room_messages(
            self,
            room_id: int,
            limit: int = 50,
            offset: int = 0,
    ) -> List[Message]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.room_id==room_id)
            .order_by(MessageModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_last_message(self, room_id: int) -> Optional[Message]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.room_id==room_id)
            .order_by(MessageModel.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

