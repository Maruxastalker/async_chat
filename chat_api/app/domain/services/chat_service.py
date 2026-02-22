from typing import List, Optional

from chat_api.app.domain.entities.message import Message
from chat_api.app.domain.entities.room import Room
from chat_api.app.core.exceptions import RoomNotFound, NotRoomMember
from chat_api.app.domain.repositories.message_repository import IMessageRepository
from chat_api.app.domain.repositories.room_repository import IRoomRepository
from chat_api.app.domain.value_objects.message_content import MessageContent


class ChatService:
    """
        Сервис работы с чатом и сообщениями.
    """

    def __init__(self, message_repo: IMessageRepository, room_repo: IRoomRepository):
        self.message_repo = message_repo
        self.room_repo = room_repo

    async def send_message(
            self,
            content: str,
            room_id: int,
            user_id: int,
            message_type: str = "text",
            reply_to_id: Optional[int] = None,
    ) -> Message:
        """
               Отправить сообщение в комнату.

               Args:
                   content: Текст сообщения
                   room_id: ID комнаты
                   user_id: ID отправителя
                   message_type: Тип сообщения
                   reply_to_id: Ответ на сообщение

               Returns:
                   Message: Отправленное сообщение

               Raises:
                   RoomNotFound: Если комната не найдена
                   NotRoomMember: Если пользователь не участник комнаты
        """

        room = await self.room_repo.get_by_id(room_id=room_id)
        if not room:
            raise RoomNotFound(room_id=room_id)

        participants = await self.room_repo.get_room_participants(room_id)
        if user_id not in participants:
            raise NotRoomMember(user_id=user_id, room_id=room_id)

        content_vo = MessageContent(content)

        message = Message(
            content=str(content_vo),
            room_id=room_id,
            user_id=user_id,
            message_type=message_type,
            reply_to_id=reply_to_id,
        )

        return await self.message_repo.create(message)

    async def get_room_messages(
            self,
            room_id: int,
            user_id: int,
            limit: int = 50,
            offset: int = 0
    ) -> List[Message]:
        """
        Получить сообщения комнаты.

        Args:
            room_id: ID комнаты
            user_id: ID пользователя (для проверки прав)
            limit: Количество сообщений
            offset: Смещение

        Returns:
            List[Message]: Список сообщений

        Raises:
            RoomNotFound: Если комната не найдена
            NotRoomMember: Если пользователь не участник
        """

        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise RoomNotFound(room_id=room_id)

        participants = await self.room_repo.get_room_participants(room_id)
        if user_id not in participants:
            raise NotRoomMember(user_id=user_id, room_id=room_id)


        return await self.message_repo.get_room_messages(
            room_id=room_id,
            limit=limit,
            offset=offset
        )


