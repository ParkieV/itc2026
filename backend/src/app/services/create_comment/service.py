from datetime import datetime
from zoneinfo import ZoneInfo

from entities.comment import Comment
from repositories.inmemory_comments_repo import AsyncInMemoryCommentsRepository
from services.get_pdf_document.service import GetPdfDocumentService
from services.get_stage_by_id.service import GetStageByIdService
from services.get_user.service import GetUserService


class CreateCommentService:
    def __init__(
        self,
        comments_repo: AsyncInMemoryCommentsRepository,
        get_pdf_document_service: GetPdfDocumentService,
        get_stage_by_id_service: GetStageByIdService,
        get_user_service: GetUserService,
    ):
        self._comments_repo = comments_repo
        self._get_pdf_document_service = get_pdf_document_service
        self._get_stage_by_id_service = get_stage_by_id_service
        self._get_user_service = get_user_service

    @staticmethod
    def _now_msk_timestamp() -> int:
        return int(datetime.now(ZoneInfo("Europe/Moscow")).timestamp())

    async def execute(
        self,
        doc_id: int,
        stage_id: int,
        user_id: int,
        subject: str,
        content: str,
    ) -> None:
        await self._get_pdf_document_service.execute(doc_id)
        await self._get_stage_by_id_service.execute(stage_id)
        await self._get_user_service.execute(user_id)
        await self._comments_repo.add(
            Comment(
                doc_id=doc_id,
                stage_id=stage_id,
                user_id=user_id,
                subject=subject,
                content=content,
                created_at=self._now_msk_timestamp(),
            )
        )
