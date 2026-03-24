from entities.review import Review
from repositories.inmemory_reviews_repo import AsyncInMemoryReviewsRepository
from services.get_pdf_document.service import GetPdfDocumentService
from services.get_stage_by_id.service import GetStageByIdService
from services.get_user.service import GetUserService
from .exceptions import ReviewAlreadyExists


class SetupReviewerService:
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

    async def execute(self, doc_id: int, user_id: int, stage_id: int) -> None:
        await self._get_user_service.execute(user_id)
        await self._get_stage_by_id_service.execute(stage_id)
        await self._get_pdf_document_service.execute(doc_id)
        existing = await self._reviews_repo.get_list_by_stage_and_doc(stage_id, doc_id)
        if any(r.user_id == user_id for r in existing):
            raise ReviewAlreadyExists(
                f"review for doc_id={doc_id}, user_id={user_id}, stage_id={stage_id} already exists"
            )
        await self._reviews_repo.add(
            Review(
                stage_id=stage_id,
                doc_id=doc_id,
                user_id=user_id,
                is_viewed=False,
                status=None,
            )
        )
