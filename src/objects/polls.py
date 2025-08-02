from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.models import Poll

from .base_service import BaseService


class PollService(BaseService[Poll]):
    """
    CRUD для опросов.
    """

    model = Poll

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        question: str,
        created_by: int | None = None,
    ) -> Poll:
        p = Poll(question=question, created_by=created_by)
        session.add(p)

        await session.commit()
        await session.refresh(p)

        return p
