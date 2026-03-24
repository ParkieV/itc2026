from entities.document_detail import DocumentDetail
from repositories.inmemory_comments_repo import AsyncInMemoryCommentsRepository
from repositories.inmemory_reviews_repo import AsyncInMemoryReviewsRepository
from services.get_pdf_document.service import GetPdfDocumentService


class GetDocumentDetailUseCase:
    def __init__(
        self,
        get_pdf_document_service: GetPdfDocumentService,
        reviews_repo: AsyncInMemoryReviewsRepository,
        comments_repo: AsyncInMemoryCommentsRepository,
    ):
        self._get_pdf_document_service = get_pdf_document_service
        self._reviews_repo = reviews_repo
        self._comments_repo = comments_repo

    async def execute(self, doc_id: int) -> DocumentDetail:
        document = await self._get_pdf_document_service.execute(doc_id)
        stage_id = document.stage_id
        reviews = await self._reviews_repo.get_list_by_stage_and_doc(stage_id, doc_id)
        comments = await self._comments_repo.get_by_doc_and_stage_id(doc_id, stage_id)
        return DocumentDetail(document=document, reviews=reviews, comments=comments)
