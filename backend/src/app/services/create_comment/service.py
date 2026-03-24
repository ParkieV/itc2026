from datetime import datetime
from zoneinfo import ZoneInfo

from entities.comment import Comment
from repositories.inmemory_comments_repo import AsyncInMemoryCommentsRepository
from services.comment_exceptions import CommentNotFound
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
        xfdf: str,
        reply_to: int | None = None,
    ) -> None:
        await self._get_pdf_document_service.execute(doc_id)
        await self._get_stage_by_id_service.execute(stage_id)
        await self._get_user_service.execute(user_id)
        if reply_to is not None:
            parent = await self._comments_repo.get_by_doc_and_comment_id(doc_id, reply_to)
            if parent is None:
                raise CommentNotFound(doc_id, reply_to)
        await self._comments_repo.add(
            Comment(
                comment_id=0,
                doc_id=doc_id,
                stage_id=stage_id,
                user_id=user_id,
                subject=subject,
                content=content,
                xfdf=xfdf,
                created_at=self._now_msk_timestamp(),
                reply_to=reply_to,
            )
        )
