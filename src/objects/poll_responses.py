from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.models import PollResponse

from .base_service import BaseService


class PollResponseService(BaseService[PollResponse]):
    """
    CRUD для ответов на опросы.
    """

    model = PollResponse

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        poll_id: int,
        user_id: int,
        option_id: int,
    ) -> PollResponse:
        resp = PollResponse(poll_id=poll_id, user_id=user_id, option_id=option_id)
        session.add(resp)

        await session.commit()
        await session.refresh(resp)

        return resp
