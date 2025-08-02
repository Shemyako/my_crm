from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.models import Event

from .base_service import BaseService


class EventService(BaseService[Event]):
    """
    CRUD для событий.
    """

    model = Event

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        title: str,
        event_type_id: int,
        start_time: datetime,
        end_time: datetime,
        description: str | None = None,
        location: str | None = None,
        created_by: int | None = None,
    ) -> Event:
        ev = Event(
            title=title,
            event_type_id=event_type_id,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location,
            created_by=created_by,
        )
        session.add(ev)

        await session.commit()
        await session.refresh(ev)

        return ev
