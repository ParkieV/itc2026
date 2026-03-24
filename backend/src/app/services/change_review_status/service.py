from entities.review_status import ReviewStatus
from repositories.inmemory_reviews_repo import AsyncInMemoryReviewsRepository
from services.get_pdf_document.service import GetPdfDocumentService
from services.get_stage_by_id.service import GetStageByIdService
from services.get_user.service import GetUserService


class ChangeReviewStatusService:
    def __init__(
        self,
        reviews_repo: AsyncInMemoryReviewsRepository,
        get_user_service: GetUserService,
        get_stage_by_id_service: GetStageByIdService,
        get_pdf_document_service: GetPdfDocumentService,
    ):
        self._reviews_repo = reviews_repo
        self._get_user_service = get_user_service
        self._get_stage_by_id_service = get_stage_by_id_service
        self._get_pdf_document_service = get_pdf_document_service

    async def execute(
        self,
        doc_id: int,
        user_id: int,
        stage_id: int,
        status: ReviewStatus,
    ) -> int:
        await self._get_user_service.execute(user_id)
        await self._get_stage_by_id_service.execute(stage_id)
        await self._get_pdf_document_service.execute(doc_id)
        return await self._reviews_repo.update_status(
            stage_id=stage_id,
            doc_id=doc_id,
            user_id=user_id,
            status=status,
        )
