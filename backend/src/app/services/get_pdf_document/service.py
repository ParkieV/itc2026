from entities import Document
from repositories.inmemory_document_repo import InMemoryDocumentRepository
from services.get_pdf_document.exceptions import DocumentNotFound, DocumentNotAllowed


class GetPdfDocumentService:
    def __init__(
            self,
            document_repo: InMemoryDocumentRepository
    ):
        self._document_repo = document_repo

    async def execute(self, document_id: int) -> Document:
        if (document := self._document_repo.get_document(document_id)) is None:
            raise DocumentNotFound(f"Document with id {document_id} not found")

        return document
