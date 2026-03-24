from entities import Document
from repositories.inmemory_document_repo import InMemoryDocumentRepository


class AddDocumentService:
    def __init__(
            self,
            document_repo: InMemoryDocumentRepository,
    ):
        self._document_repo = document_repo

    async def execute(self, document: Document) -> int:
        document_id = self._document_repo.get_next_document_id()
        self._document_repo.add_document(document)
        return document_id