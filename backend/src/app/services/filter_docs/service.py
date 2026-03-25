from typing import Literal

from repositories.inmemory_document_repo import InMemoryDocumentRepository
from entities import Document


class FilterDocsService:
    def __init__(
        self,
        document_repo: InMemoryDocumentRepository
        ):
        self._document_repo = document_repo

    async def execute(
        self, document_id: int,
        roles: list[Literal['author', 'reviewer']] | None = None,
        review_statuses: list[Literal['']] | None = None,
        categories: list[Literal['']] | None = None,
        doc_statuses: list[Literal['']] | None = None,
        ) -> list[Document]:
        return await self._document_repo.get_document_with_filters(document_id)