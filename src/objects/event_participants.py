from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.models import EventParticipant

from .base_service import BaseService


class EventParticipantService(BaseService[EventParticipant]):
    """
    CRUD для участников событий.
    """

    model = EventParticipant

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        event_id: int,
        user_id: int,
        reminder_15min: bool | None = None,
        reminder_1h: bool | None = None,
        reminder_1d: bool | None = None,
    ) -> EventParticipant:
        ep = EventParticipant(
            event_id=event_id,
            user_id=user_id,
            reminder_15min=reminder_15min if reminder_15min is not None else True,
            reminder_1h=reminder_1h if reminder_1h is not None else False,
            reminder_1d=reminder_1d if reminder_1d is not None else False,
        )
        session.add(ep)

        await session.commit()
        await session.refresh(ep)

        return ep
