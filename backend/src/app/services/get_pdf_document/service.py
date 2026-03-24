from entities import Document
from repositories.inmemory_document_files_repo import InMemoryDocumentFilesRepository
from repositories.inmemory_document_repo import InMemoryDocumentRepository
from services.get_pdf_document.exceptions import DocumentNotFound


class GetPdfDocumentService:
    def __init__(
            self,
            document_repo: InMemoryDocumentRepository,
            document_files_repo: InMemoryDocumentFilesRepository,
    ):
        self._document_repo = document_repo
        self._document_files_repo = document_files_repo

    async def execute(self, document_id: int) -> Document:
        if (document := self._document_repo.get_document(document_id)) is None:
            raise DocumentNotFound(f"Document with id {document_id} not found")

        if document.file_id is None:
            return document

        if (paths := self._document_files_repo.get_paths(document.file_id)) is None:
            return document

        return Document(
            title=document.title,
            authors=document.authors,
            file_id=document.file_id,
            pdf_file_id=document.pdf_file_id,
        )
