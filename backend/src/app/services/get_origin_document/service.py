from entities import Document
from repositories.inmemory_document_repo import InMemoryDocumentRepository
from services.get_origin_document.exceptions import DocumentNotFound, DocumentNotAllowed


class GetOriginDocumentService:
    def __init__(
            self,
            document_repo: InMemoryDocumentRepository
    ):
        self._document_repo = document_repo

    async def execute(self, document_id: int, client_id: int) -> Document:
        if (document := self._document_repo.get_document(document_id)) is None:
            raise DocumentNotFound(f"Document with id {document_id} not found")

        if client_id not in document.authors:
            raise DocumentNotAllowed(f"Client with id {client_id} is not allowed to access document with id {document_id}")

        return document
