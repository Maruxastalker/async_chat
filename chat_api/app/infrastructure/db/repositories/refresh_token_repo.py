from typing import Optional, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from chat_api.app.domain.entities.refresh_token import RefreshToken
from chat_api.app.domain.repositories.refresh_token_repository import IRefreshTokenRepository
from chat_api.app.infrastructure.db.models import RefreshTokenModel


class RefreshTokenRepository(IRefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain(model: RefreshTokenModel) -> RefreshToken:
        return RefreshToken(
            id=model.id,
            user_id=model.user_id,
            token=model.token,
            expires_at=model.expires_at,
            is_revoked=model.is_revoked,
            created_at=model.created_at,
        )
    async def get_by_id(self, token_id: int) -> Optional[RefreshToken]:
        model = await self.session.get(RefreshTokenModel, token_id)
        if not model:
            return None
        return self._to_domain(model)

    async def create(self, token: RefreshToken) -> RefreshToken:
        model = RefreshTokenModel(
            user_id=token.user_id,
            token=token.token,
            expires_at=token.expires_at,
            is_revoked=token.is_revoked,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def update(self, token: RefreshToken) -> Optional[RefreshToken]:
        model = await self.session.get(RefreshTokenModel, token.id)
        if not model:
            return None

        model.token = token.token
        model.expires_at = token.expires_at
        model.is_revoked=token.is_revoked

        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def delete(self, token_id: int) -> bool:
        model = await self.session.get(RefreshTokenModel, token_id)
        if not model:
            return False
        await self.session.delete(model)
        return True

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token==token)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def revoke(self, token_id: int) -> bool:
        model = await self.session.get(RefreshTokenModel, token_id)

        if not model:
            return False

        model.is_revoked = True

        self.session.add(model)
        await self.session.flush()
        return True

    async def revoke_all_user_tokens(self, user_id: int) -> None:
        stmt = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .values(is_revoked=True)
        )
        await self.session.execute(stmt)

    async def get_user_tokens(self, user_id: int) -> List[RefreshToken]:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.user_id==user_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]
