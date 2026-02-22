from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chat_api.app.domain.entities.user import User
from chat_api.app.domain.repositories.user_repository import IUserRepository
from ..models import UserModel


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            is_online=model.is_online,
            last_seen=model.last_seen,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_model(entity: User) -> UserModel:
        model = UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            hashed_password=entity.hashed_password,
            is_active=entity.is_active,
            is_online=entity.is_online,
            last_seen=entity.last_seen,
        )
        return model

    async def get_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        model: Optional[UserModel] = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def create(self, user: User) -> User:
        model = UserModel(
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_online=user.is_online,
            last_seen=user.last_seen,
        )

        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def update(self, user: User) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        model: Optional[UserModel] = result.scalar_one_or_none()
        if not model:
            return None

        model.username = user.username
        model.email = user.email
        model.hashed_password = user.hashed_password
        model.is_active = user.is_active
        model.is_online = user.is_online
        model.last_seen = user.last_seen

        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def delete(self, user_id: int) -> bool:
        model = self.session.get(UserModel, user_id)
        if not model:
            return False
        await self.session.delete(model)
        return True

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.username==username)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email==email)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def search_users(self, query: str, limit: int = 10) -> List[User]:
        like_pattern = f"%{query}"
        stmt = (
            select(UserModel)
            .where(UserModel.username.ilike(like_pattern))
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

