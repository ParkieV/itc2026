from entities.document import Document
from repositories.inmemory_document_repo import InMemoryDocumentRepository
from .exceptions import DocumentNotFound


class ChangeDocumentStageService:
    def __init__(self, document_repo: InMemoryDocumentRepository):
        self._document_repo = document_repo

    async def execute(self, doc_id: int, document: Document) -> None:
        try:
            self._document_repo.patch_document(document, doc_id)
        except ValueError as err:
            raise DocumentNotFound(f"Document with id {doc_id} not found") from err
