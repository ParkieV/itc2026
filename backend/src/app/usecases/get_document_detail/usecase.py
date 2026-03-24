from entities.document_detail import DocumentDetail
from repositories.inmemory_reviews_repo import AsyncInMemoryReviewsRepository
from services.get_pdf_document.service import GetPdfDocumentService


class GetDocumentDetailUseCase:
    def __init__(
        self,
        get_pdf_document_service: GetPdfDocumentService,
        reviews_repo: AsyncInMemoryReviewsRepository,
    ):
        self._get_pdf_document_service = get_pdf_document_service
        self._reviews_repo = reviews_repo

    async def execute(self, doc_id: int) -> DocumentDetail:
        document = await self._get_pdf_document_service.execute(doc_id)
        reviews = await self._reviews_repo.get_list_by_stage_and_doc(document.stage_id, doc_id)
        return DocumentDetail(document=document, reviews=reviews)
