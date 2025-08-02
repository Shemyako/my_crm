from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.models import Role

from .base_service import BaseService


class RoleService(BaseService[Role]):
    """
    Бизнес-логика для работы с ролями: создание, получение, обновление, удаление.
    Использует асинхронные сессии SQLAlchemy.
    """

    model = Role

    @classmethod
    async def create_role(
        cls,
        session: AsyncSession,
        name: str,
        description: str | None = None,
    ) -> Role:
        """Создать новую роль."""
        role = Role(name=name, description=description)
        session.add(role)

        await session.commit()
        await session.refresh(role)

        return role
