from typing import List
from chat_api.app.domain.entities.room import Room
from chat_api.app.domain.entities.user import User
from chat_api.app.core.exceptions import RoomNotFound, ForbiddenAction
from chat_api.app.domain.repositories.room_repository import IRoomRepository
from chat_api.app.domain.repositories.user_repository import IUserRepository


class RoomService:
    """
    Сервис работы с комнатами
    """

    def __init__(
            self,
            room_repo:IRoomRepository,
            user_repo:IUserRepository,
    ):
        self.room_repo = room_repo
        self.user_repo = user_repo

    async def create_room(
            self,
            name: str,
            description: str,
            owner_id: int,
            is_private: bool = False,
            max_participants: int = 0,
    ) -> Room:
        """
                Создать новую комнату.

                Args:
                    name: Название комнаты
                    owner_id: ID создателя
                    is_private: Приватная ли комната
                    max_participants: Максимум участников (0 = без лимита)

                Returns:
                    Room: Созданная комната
        """

        owner = await self.user_repo.get_by_id(owner_id)
        if not owner:
            raise ValueError(f"User {owner_id} not found")

        room = Room(
            name=name,
            owner_id=owner_id,
            description=description,
            is_private=is_private,
            max_participants=max_participants,
        )

        saved_room = await self.room_repo.create(room)

        await self.room_repo.add_participant(saved_room.id,owner_id)
        return saved_room

    async def get_room(self, room_id: int) -> Room:
        """
                Получить комнату по ID.

                Args:
                    room_id: ID комнаты

                Returns:
                    Room: Доменная сущность комнаты

                Raises:
                    RoomNotFound: Если комната не найдена
        """

        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise RoomNotFound(room_id=room_id)
        return room

    async def get_user_rooms(self, user_id: int) -> List[Room]:
        """
                Получить все комнаты пользователя.

                Args:
                    user_id: ID пользователя

                Returns:
                    List[Room]: Список комнат
        """
        return await self.room_repo.get_user_rooms(user_id)

    async def add_user_to_room(self, room_id: int, user_id: int, inviter_id) -> None:
        """
                Добавить пользователя в комнату.

                Args:
                    room_id: ID комнаты
                    user_id: ID добавляемого пользователя
                    inviter_id: ID пользователя, который добавляет

                Raises:
                    RoomNotFound: Если комната не найдена
                    ForbiddenAction: Если у inviter нет прав
        """
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise RoomNotFound(room_id=room_id)

        if room.is_private:
            if inviter_id != room.owner_id:
                raise ForbiddenAction(
                    action="add_user_to_private_room",
                    reason="Only room owner can add users to private rooms"
                )

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        await self.room_repo.add_participant(room_id,user_id)

    async def remove_user_from_room(
            self,
            room_id: int,
            user_id: int,
            remover_id: int
    ) -> None:
        """
        Удалить пользователя из комнаты.

        Args:
            room_id: ID комнаты
            user_id: ID удаляемого пользователя
            remover_id: ID пользователя, который удаляет

        Raises:
            ForbiddenAction: Если у remover нет прав
        """
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise RoomNotFound(room_id=room_id)

        if remover_id != room.owner_id and remover_id != user_id:
            raise ForbiddenAction(
                action="remove_user_from_room",
                reason="Only room owner or user themselves can remove"
            )

        if user_id == room.owner_id:
            raise ForbiddenAction(
                action="remove_room_owner",
                reason="Cannot remove room owner from room"
            )

        await self.room_repo.remove_participant(room_id, user_id)