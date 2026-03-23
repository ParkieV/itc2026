from entities import Document
from repositories.inmemory_document_repo import InMemoryDocumentRepository
from repositories.inmemory_user_repo import AsyncInMemoryUserRepository


class AddDocumentService:
    def __init__(
            self,
            document_repo: InMemoryDocumentRepository,
    ):
        self._document_repo = document_repo

    async def execute(self, document: Document) -> None:
        self._document_repo.add_document(document)