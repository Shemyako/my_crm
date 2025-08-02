from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseService(ABC, Generic[ModelType]):
    """
    Абстрактный базовый класс для CRUD сервисов.
    """

    model: type[ModelType]

    @classmethod
    @abstractmethod
    async def create(cls, session: AsyncSession, *args, **kwargs) -> ModelType:
        pass

    @classmethod
    async def get(cls, session: AsyncSession, obj_id: int) -> ModelType | None:
        result = await session.execute(select(cls.model).where(cls.model.id == obj_id))
        return result.scalars().one_or_none()

    @classmethod
    async def list(cls, session: AsyncSession) -> list[ModelType]:
        result = await session.execute(select(cls.model))
        return result.scalars().all()

    @classmethod
    async def update(cls, session: AsyncSession, obj_id: int, **kwargs: object) -> ModelType | None:
        obj = await cls.get(session, obj_id)
        if not obj:
            return None
        for key, value in kwargs.items():
            setattr(obj, key, value)
        await session.commit()
        await session.refresh(obj)
        return obj

    @classmethod
    async def delete(cls, session: AsyncSession, obj_id: int) -> bool:
        obj = await cls.get(session, obj_id)
        if not obj:
            return False
        await session.delete(obj)
        await session.commit()
        return True
