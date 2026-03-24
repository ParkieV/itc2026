from entities.review import Review
from repositories.inmemory_reviews_repo import AsyncInMemoryReviewsRepository
from services.get_pdf_document.service import GetPdfDocumentService
from services.get_user.service import GetUserService


class GetStageDocReviewersService:
    def __init__(
        self,
        reviews_repo: AsyncInMemoryReviewsRepository,
        get_user_service: GetUserService,
        get_pdf_document_service: GetPdfDocumentService,
    ):
        self._reviews_repo = reviews_repo
        self._get_user_service = get_user_service
        self._get_pdf_document_service = get_pdf_document_service

    async def execute(self, user_id: int, doc_id: int) -> list[Review]:
        await self._get_user_service.execute(user_id)
        await self._get_pdf_document_service.execute(doc_id)
        reviews = await self._reviews_repo.get_list_by_user_id(user_id)
        return [review for review in reviews if review.doc_id == doc_id]
