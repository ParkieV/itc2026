from entities.comment import Comment
from repositories.inmemory_comments_repo import AsyncInMemoryCommentsRepository
from services.get_pdf_document.service import GetPdfDocumentService
from services.get_stage_by_id.service import GetStageByIdService


class GetCommentsByDocService:
    def __init__(
        self,
        comments_repo: AsyncInMemoryCommentsRepository,
        get_pdf_document_service: GetPdfDocumentService,
        get_stage_by_id_service: GetStageByIdService,
    ):
        self._comments_repo = comments_repo
        self._get_pdf_document_service = get_pdf_document_service
        self._get_stage_by_id_service = get_stage_by_id_service

    async def execute(self, doc_id: int) -> list[Comment]:
        document = await self._get_pdf_document_service.execute(doc_id)
        await self._get_stage_by_id_service.execute(document.stage_id)
        return await self._comments_repo.get_by_doc_id(doc_id)
