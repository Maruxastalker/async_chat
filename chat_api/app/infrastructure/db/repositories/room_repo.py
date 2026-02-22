from typing import Optional, List

from sqlalchemy import select, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from chat_api.app.domain.entities.room import Room
from chat_api.app.domain.repositories.room_repository import IRoomRepository
from chat_api.app.infrastructure.db.models import RoomModel, UserRoomModel


class RoomRepository(IRoomRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain(model: RoomModel) -> Room:
        return Room(
            id=model.id,
            name=model.name,
            owner_id=model.owner_id,
            description=model.description,
            is_private=model.is_private,
            max_participants=model.max_participants,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, room_id: int) -> Optional[Room]:
        model = await self.session.get(RoomModel, room_id)
        if not model:
            return None
        return self._to_domain(model)

    async def create(self, room: Room) -> Room:
        model = RoomModel(
            name=room.name,
            owner_id=room.owner_id,
            description=room.description,
            is_private=room.is_private,
            max_participants=room.max_participants,
        )

        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def update(self, room: Room) -> Optional[Room]:
        model = await self.session.get(RoomModel, room.id)
        if not model:
            return None

        model.name = room.name
        model.description = room.description
        model.is_private = room.is_private
        model.max_participants = room.max_participants

        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def delete(self, room_id: int) -> bool:
        model = await self.session.get(RoomModel, room_id)
        if not model:
            return False
        await self.session.delete(model)
        return True

    async def add_participant(self, room_id: int, user_id: int) -> None:
        assoc = UserRoomModel(user_id=user_id, room_id=room_id)
        self.session.add(assoc)

        await self.session.flush()

    async def get_user_rooms(self, user_id: int) -> List[Room]:
        stmt = (
            select(RoomModel)
            .join(UserRoomModel, UserRoomModel.room_id==RoomModel.id)
            .where(UserRoomModel.user_id==user_id)
        )
        result = await self.session.execute(stmt)
        rooms = result.scalars().all()
        return [self._to_domain(r) for r in rooms]

    async def remove_participant(self, room_id: int, user_id: int) -> None:
        stmt = (
            delete(UserRoomModel)
            .where(
                UserRoomModel.user_id==user_id,
                UserRoomModel.room_id==room_id
            )
        )

        await self.session.execute(stmt)

    async def get_room_participants(self, room_id: int) -> List[int]:
        stmt = select(UserRoomModel.user_id).where(UserRoomModel.room_id==room_id)
        result = await self.session.execute(stmt)
        users_list = result.scalars().all()
        return list(users_list)