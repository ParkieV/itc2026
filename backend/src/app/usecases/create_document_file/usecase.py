from entities import Document
from services.add_document.exceptions import InvalidAuthorId
from services.add_origin_document_file.service import AddOriginDocumentFileService, UploadedFileLike
from services.authenticate_user.exceptions import UserNotFound
from services.get_user.service import GetUserService
from services.notification import NotificationEvent, Notifier
from services.save_pdf_document_file.service import SavePdfDocumentFileService
from services.add_document.service import AddDocumentService


class CreateDocumentFileUseCase:
    def __init__(
        self,
        get_user_service: GetUserService,
        add_document_service: AddDocumentService,
        add_origin_document_file_service: AddOriginDocumentFileService,
        save_pdf_document_file_service: SavePdfDocumentFileService,
        notifier: Notifier,
    ):
        self._get_user_service = get_user_service
        self._add_document_service = add_document_service
        self._add_origin_document_file_service = add_origin_document_file_service
        self._save_pdf_document_file_service = save_pdf_document_file_service
        self._notifier = notifier

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
        document_id = await self._add_document_service.execute(
            Document(
                title=document.title,
                authors=document.authors,
                file_id=file_id,
                pdf_file_id=pdf_file_id,
            )
        )
        await self._notifier.notify(
            NotificationEvent(
                event_type="document.file_created",
                subject=f"Новый документ: {document.title}",
                body=(
                    f"Загружен документ «{document.title}» (id={document_id}). "
                    f"Авторы (id): {', '.join(str(a) for a in document.authors)}."
                ),
                payload={
                    "event_type": "document.file_created",
                    "document_id": document_id,
                    "title": document.title,
                    "authors": list(document.authors),
                    "file_id": file_id,
                    "pdf_file_id": pdf_file_id,
                },
                user_ids=tuple(document.authors),
            )
        )
        return document_id
