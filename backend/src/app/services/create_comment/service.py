from entities.comment import Comment
from repositories.inmemory_comments_repo import AsyncInMemoryCommentsRepository
from services.comment_exceptions import CommentNotFound
from services.get_pdf_document.service import GetPdfDocumentService
from services.get_stage_by_id.service import GetStageByIdService
from services.get_user.service import GetUserService
from services.notification import NotificationEvent, Notifier
from utils.datetime_iso import now_iso_msk

_PUBLIC_DOCUMENT_PDF_URL_PREFIX = "http://itc2026.parkie.tech/pdf"


class CreateCommentService:
    def __init__(
        self,
        comments_repo: AsyncInMemoryCommentsRepository,
        get_pdf_document_service: GetPdfDocumentService,
        get_stage_by_id_service: GetStageByIdService,
        get_user_service: GetUserService,
        notifier: Notifier,
    ):
        self._comments_repo = comments_repo
        self._get_pdf_document_service = get_pdf_document_service
        self._get_stage_by_id_service = get_stage_by_id_service
        self._get_user_service = get_user_service
        self._notifier = notifier

    async def execute(
        self,
        doc_id: int,
        stage_id: int,
        user_id: int,
        remark: str | None,
        proposal: str | None,
        justification: str | None,
        xfdf: str,
        reply_to: int | None = None,
    ) -> None:
        document = await self._get_pdf_document_service.execute(doc_id)
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
                remark=remark,
                proposal=proposal,
                justification=justification,
                developer_response=None,
                xfdf=xfdf,
                created_at=now_iso_msk(),
                reply_to=reply_to,
            )
        )
        doc_url = f"{_PUBLIC_DOCUMENT_PDF_URL_PREFIX}/{doc_id}"
        recipient_ids = tuple(a for a in document.authors if a != user_id)
        if recipient_ids:
            await self._notifier.notify(
                NotificationEvent(
                    event_type="document.comment_created",
                    subject="Новый комментарий к документу",
                    body=(
                        f"К документу «{document.title}» добавлен комментарий.\n"
                        f"Открыть PDF на сайте: {doc_url}"
                    ),
                    payload={
                        "event_type": "document.comment_created",
                        "document_id": doc_id,
                        "document_url": doc_url,
                        "comment_author_user_id": user_id,
                    },
                    user_ids=recipient_ids,
                )
            )
