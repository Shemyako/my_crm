from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.models import Document

from .base_service import BaseService


class DocumentService(BaseService[Document]):
    """
    CRUD для документов.
    """

    model = Document

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        title: str,
        description: str | None = None,
        file_url: str | None = None,
        created_by: int | None = None,
    ) -> Document:
        doc = Document(
            title=title, description=description, file_url=file_url, created_by=created_by
        )
        session.add(doc)

        await session.commit()
        await session.refresh(doc)

        return doc
