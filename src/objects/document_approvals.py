from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.models import DocumentApproval

from .base_service import BaseService


class DocumentApprovalService(BaseService[DocumentApproval]):
    """
    CRUD для согласований документов.
    """

    model = DocumentApproval

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        document_id: int,
        approver_id: int,
        order_index: int = 0,
    ) -> DocumentApproval:
        """Создать запись по согласованию документа (назначить согласующего)."""
        da = cls.model(
            document_id=document_id,
            approver_id=approver_id,
            order_index=order_index,
            approved=False,
        )
        session.add(da)

        await session.commit()
        await session.refresh(da)

        return da

    @staticmethod
    async def approve(
        session: AsyncSession,
        approval_id: int,
        approved: bool = True,
    ) -> DocumentApproval | None:
        da = await DocumentApprovalService.get(session, approval_id)
        if not da:
            return None

        da.approved = approved
        da.approved_at = datetime.now(tz=timezone.utc)

        await session.commit()
        await session.refresh(da)

        return da
