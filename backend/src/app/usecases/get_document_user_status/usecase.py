from entities.document_user_status import DocumentUserStatus
from repositories.inmemory_comments_repo import AsyncInMemoryCommentsRepository
from repositories.inmemory_reviews_repo import AsyncInMemoryReviewsRepository
from services.get_pdf_document.service import GetPdfDocumentService

from .exceptions import DocumentStatusAccessDenied


class GetDocumentUserStatusUseCase:
    def __init__(
        self,
        get_pdf_document_service: GetPdfDocumentService,
        comments_repo: AsyncInMemoryCommentsRepository,
        reviews_repo: AsyncInMemoryReviewsRepository,
    ):
        self._get_pdf_document_service = get_pdf_document_service
        self._comments_repo = comments_repo
        self._reviews_repo = reviews_repo

    def _status_for_creator(self, comments, reviews) -> DocumentUserStatus:
        if any(c.status is None for c in comments):
            return DocumentUserStatus.NEW_COMMENT
        any_viewed = any(r.is_viewed for r in reviews)
        if not comments and not any_viewed:
            return DocumentUserStatus.WAITING
        if not any_viewed:
            return DocumentUserStatus.NOT_VIEWED
        return DocumentUserStatus.VIEWED

    def _status_for_expert(self, comments, user_id: int) -> DocumentUserStatus:
        mine = [c for c in comments if c.user_id == user_id]
        if not mine:
            return DocumentUserStatus.ACTION_REQUIRED
        return DocumentUserStatus.SENT

    async def execute(self, doc_id: int, user_id: int) -> DocumentUserStatus:
        document = await self._get_pdf_document_service.execute(doc_id)

        stage_id = document.stage_id
        comments = await self._comments_repo.get_by_doc_and_stage_id(doc_id, stage_id)
        reviews = await self._reviews_repo.get_list_by_stage_and_doc(stage_id, doc_id)

        reviewer_ids = {r.user_id for r in reviews}

        if user_id in document.authors:
            return self._status_for_creator(comments, reviews)
        if user_id in reviewer_ids:
            return self._status_for_expert(comments, user_id)
        raise DocumentStatusAccessDenied(
            f"User {user_id} is neither an author nor a reviewer for doc_id={doc_id} at stage_id={stage_id}",
        )

    async def status_for_user(self, doc_id: int, user_id: int) -> DocumentUserStatus | None:
        """Статус для пользователя; ``None``, если он не автор и не ревьюер по документу на этапе."""
        try:
            return await self.execute(doc_id, user_id)
        except DocumentStatusAccessDenied:
            return None
