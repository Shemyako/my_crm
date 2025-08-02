from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.models import Permission

from .base_service import BaseService


class PermissionService(BaseService[Permission]):
    """
    Бизнес-логика для работы с правами: создание, получение, обновление, удаление.
    Использует асинхронные сессии SQLAlchemy.
    """

    model = Permission

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        code: str,
        description: str | None = None,
    ) -> Permission:
        """Создать новое право (permission)."""
        permission = Permission(code=code, description=description)
        session.add(permission)

        await session.commit()
        await session.refresh(permission)

        return permission
