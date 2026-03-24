from entities.document import Document
from entities.review_status import ReviewStatus
from repositories.inmemory_reviews_repo import AsyncInMemoryReviewsRepository
from services.change_doc_stage.exceptions import (
    DocumentNotFound,
    DocumentRevisionRequired,
    InvalidTargetStage,
    ReviewsNotAllAccepted,
    StageNotFound,
)
from services.change_doc_stage.service import ChangeDocumentStageService
from services.get_stage_by_id.exceptions import StageNotFound as GetStageByIdStageNotFound
from services.get_stage_by_id.service import GetStageByIdService
from services.get_pdf_document.exceptions import DocumentNotFound as PdfDocumentNotFound
from services.get_pdf_document.service import GetPdfDocumentService


class ChangeDocumentStageUseCase:
    def __init__(
        self,
        get_pdf_document_service: GetPdfDocumentService,
        change_document_stage_service: ChangeDocumentStageService,
        get_stage_by_id_service: GetStageByIdService,
        reviews_repo: AsyncInMemoryReviewsRepository,
    ):
        self._get_pdf_document_service = get_pdf_document_service
        self._change_document_stage_service = change_document_stage_service
        self._get_stage_by_id_service = get_stage_by_id_service
        self._reviews_repo = reviews_repo

    async def execute(self, doc_id: int, stage_id: int) -> None:
        try:
            document = await self._get_pdf_document_service.execute(doc_id)
        except PdfDocumentNotFound as err:
            raise DocumentNotFound(str(err)) from err

        if document.stage_id == stage_id:
            raise InvalidTargetStage(
                f"Target stage {stage_id} is invalid: it matches current document stage",
            )

        try:
            current_stage = await self._get_stage_by_id_service.execute(document.stage_id)
        except GetStageByIdStageNotFound as err:
            raise StageNotFound(str(err)) from err

        if stage_id != current_stage.next_stage:
            raise InvalidTargetStage(
                f"Target stage {stage_id} is invalid: must be next_stage {current_stage.next_stage} "
                f"for current stage {document.stage_id}",
            )

        try:
            await self._get_stage_by_id_service.execute(stage_id)
        except GetStageByIdStageNotFound as err:
            raise StageNotFound(str(err)) from err

        reviews = await self._reviews_repo.get_list_by_stage_and_doc(
            document.stage_id,
            doc_id,
        )
        if any(r.status == ReviewStatus.DECLINED for r in reviews):
            raise DocumentRevisionRequired(
                "Требуется внести изменения в документ: есть ревью со статусом DECLINED "
                f"(doc_id={doc_id}, stage_id={document.stage_id})",
            )
        if any(r.status != ReviewStatus.ACCEPTED for r in reviews):
            raise ReviewsNotAllAccepted(
                "All reviewers for the current stage must have review status ACCEPTED "
                f"before moving the document (doc_id={doc_id}, stage_id={document.stage_id})",
            )

        updated_document = Document(
            title=document.title,
            description=document.description,
            file_id=document.file_id,
            authors=document.authors,
            stage_id=stage_id,
            created_at=document.created_at,
            modified_at=document.modified_at,
            pdf_file_id=document.pdf_file_id,
        )
        await self._change_document_stage_service.execute(doc_id, updated_document)
