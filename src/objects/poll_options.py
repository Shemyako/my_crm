from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.models import PollOption

from .base_service import BaseService


class PollOptionService(BaseService[PollOption]):
    """
    CRUD для вариантов опроса.
    """

    model = PollOption

    @classmethod
    async def create(cls, session: AsyncSession, poll_id: int, option_text: str) -> PollOption:
        opt = PollOption(poll_id=poll_id, option_text=option_text)
        session.add(opt)

        await session.commit()
        await session.refresh(opt)

        return opt
