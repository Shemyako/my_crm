from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.models import EventType

from .base_service import BaseService


class EventTypeService(BaseService[EventType]):
    """
    CRUD для типов событий.
    """

    model = EventType

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        name: str,
        description: str | None = None,
        default_reminder_15min: bool = True,
        default_reminder_1h: bool = False,
        default_reminder_1d: bool = False,
    ) -> EventType:
        et = EventType(
            name=name,
            description=description,
            default_reminder_15min=default_reminder_15min,
            default_reminder_1h=default_reminder_1h,
            default_reminder_1d=default_reminder_1d,
        )
        session.add(et)

        await session.commit()
        await session.refresh(et)

        return et
