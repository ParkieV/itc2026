from entities import Document
from services.add_document.exceptions import InvalidAuthorId
from services.add_origin_document_file.service import AddOriginDocumentFileService, UploadedFileLike
from services.authenticate_user.exceptions import UserNotFound
from services.get_user.service import GetUserService
from services.save_pdf_document_file.service import SavePdfDocumentFileService
from services.add_document.service import AddDocumentService


class CreateDocumentFileUseCase:
    def __init__(
        self,
        get_user_service: GetUserService,
        add_document_service: AddDocumentService,
        add_origin_document_file_service: AddOriginDocumentFileService,
        save_pdf_document_file_service: SavePdfDocumentFileService,
    ):
        self._get_user_service = get_user_service
        self._add_document_service = add_document_service
        self._add_origin_document_file_service = add_origin_document_file_service
        self._save_pdf_document_file_service = save_pdf_document_file_service

    async def execute(self, document: Document, upload_file: UploadedFileLike) -> int:
        for author_id in document.authors:
            try:
                await self._get_user_service.execute(author_id)
            except UserNotFound as err:
                raise InvalidAuthorId(str(err)) from err

        file_id, origin_file_path = await self._add_origin_document_file_service.execute(
            document=document,
            upload_file=upload_file,
        )
        pdf_file_id = await self._save_pdf_document_file_service.execute(
            file_id=file_id,
            document=document,
            origin_file_path=origin_file_path,
        )
        return await self._add_document_service.execute(
            Document(
                title=document.title,
                description=document.description,
                authors=document.authors,
                stage_id=document.stage_id,
                file_id=file_id,
                pdf_file_id=pdf_file_id,
            )
        )
