from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.models import User

from .base_service import BaseService


class UserService(BaseService[User]):
    """
    Бизнес-логика для работы с пользователями: создание, получение, обновление, удаление.
    Использует асинхронные сессии SQLAlchemy.
    """

    model = User

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        telegram_id: int,
        username: str | None = None,
        full_name: str | None = None,
        role_id: int | None = None,
        is_active: bool = True,
    ) -> User:
        """Создать нового пользователя."""
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            role_id=role_id,
            is_active=is_active,
        )
        session.add(user)

        await session.commit()
        await session.refresh(user)

        return user
