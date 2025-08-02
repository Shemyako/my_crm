import functools
from collections.abc import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import settings

if settings.is_test:
    engine = create_async_engine(url=settings.test_db_url)
else:
    engine = create_async_engine(url=settings.db_url)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


metadata = MetaData(schema="my_crm")


class Base(DeclarativeBase):
    metadata = metadata


def connection(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            kwargs["session"] = session
            return await func(*args, **kwargs)

    return wrapper
