from entities.comment import Comment
from entities.comment_status import CommentStatus
from repositories.inmemory_comments_repo import AsyncInMemoryCommentsRepository
from services.comment_exceptions import CommentNotFound
from services.get_pdf_document.service import GetPdfDocumentService


class PatchCommentService:
    def __init__(
        self,
        comments_repo: AsyncInMemoryCommentsRepository,
        get_pdf_document_service: GetPdfDocumentService,
    ):
        self._comments_repo = comments_repo
        self._get_pdf_document_service = get_pdf_document_service

    async def execute(
        self,
        doc_id: int,
        comment_id: int,
        *,
        is_viewed: bool | None = None,
        status: CommentStatus | None = None,
    ) -> Comment:
        await self._get_pdf_document_service.execute(doc_id)
        # None — не передаём в обновление: поле в хранилище не меняется.
        updated = await self._comments_repo.update_is_viewed_and_status(
            doc_id=doc_id,
            comment_id=comment_id,
            is_viewed=is_viewed,
            status=status,
        )
        if updated is None:
            raise CommentNotFound(doc_id, comment_id)
        return updated
