from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.models import AccessRight

from .base_service import BaseService


class AccessRightService(BaseService[AccessRight]):
    """
    Бизнес-логика для работы с индивидуальными правами доступа: CRUD операций.
    """

    model = AccessRight

    @classmethod
    async def create(cls, session: AsyncSession, user_id: int, permission_id: int) -> AccessRight:
        access = AccessRight(user_id=user_id, permission_id=permission_id)
        session.add(access)

        await session.commit()
        await session.refresh(access)

        return access
