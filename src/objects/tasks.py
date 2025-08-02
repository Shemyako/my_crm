from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.models import Task

from .base_service import BaseService


class TaskService(BaseService[Task]):
    """
    CRUD для задач.
    """

    model = Task

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        title: str,
        description: str | None = None,
        deadline: None | datetime = None,
        created_by: int | None = None,
        assigned_to: int | None = None,
    ) -> Task:
        t = Task(
            title=title,
            description=description,
            deadline=deadline,
            created_by=created_by,
            assigned_to=assigned_to,
        )
        session.add(t)

        await session.commit()
        await session.refresh(t)

        return t
