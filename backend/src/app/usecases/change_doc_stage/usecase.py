from entities.document import Document
from services.change_doc_stage.exceptions import (
    DocumentNotFound,
    InvalidTargetStage,
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
    ):
        self._get_pdf_document_service = get_pdf_document_service
        self._change_document_stage_service = change_document_stage_service
        self._get_stage_by_id_service = get_stage_by_id_service

    async def execute(self, doc_id: int, stage_id: int) -> None:
        try:
            await self._get_stage_by_id_service.execute(stage_id)
        except GetStageByIdStageNotFound as err:
            raise StageNotFound(str(err)) from err

        try:
            document = await self._get_pdf_document_service.execute(doc_id)
        except PdfDocumentNotFound as err:
            raise DocumentNotFound(str(err)) from err

        if document.stage_id == stage_id:
            raise InvalidTargetStage(
                f"Target stage {stage_id} is invalid: it matches current document stage",
            )

        updated_document = Document(
            title=document.title,
            description=document.description,
            file=document.file,
            authors=document.authors,
            stage_id=stage_id,
            created_at=document.created_at,
            modified_at=document.modified_at,
            pdf_file=document.pdf_file,
        )
        await self._change_document_stage_service.execute(doc_id, updated_document)
