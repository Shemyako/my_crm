from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.models import ChatNotification

from .base_service import BaseService


class ChatNotificationService(BaseService[ChatNotification]):
    """
    CRUD для уведомлений в чатах.
    """

    model = ChatNotification

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        user_id: int,
        event_id: int,
        chat_type: str,
        message: str,
    ) -> ChatNotification:
        cn = ChatNotification(
            user_id=user_id,
            event_id=event_id,
            chat_type=chat_type,
            message=message,
        )
        session.add(cn)

        await session.commit()
        await session.refresh(cn)

        return cn
