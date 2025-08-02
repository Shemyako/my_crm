from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.models import TimeTracking

from .base_service import BaseService


class TimeTrackingService(BaseService[TimeTracking]):
    """
    CRUD для трекера времени.
    """

    model = TimeTracking

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        user_id: int,
        description: str | None = None,
    ) -> TimeTracking:
        tt = TimeTracking(
            user_id=user_id,
            description=description,
            started_at=datetime.now(tz=timezone.utc),
        )
        session.add(tt)
        await session.commit()
        await session.refresh(tt)
        return tt

    @classmethod
    async def stop(cls, session: AsyncSession, tt_id: int) -> TimeTracking | None:
        tt = await TimeTrackingService.get(session, tt_id)
        if not tt:
            return None

        tt.ended_at = datetime.now(tz=timezone.utc)

        await session.commit()
        await session.refresh(tt)

        return tt
