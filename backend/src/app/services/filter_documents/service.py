from typing import Literal

from repositories.inmemory_document_repo import InMemoryDocumentRepository
from entities import Document


class FilterDocumentsService:
    def __init__(
        self,
        document_repo: InMemoryDocumentRepository
        ):
        self._document_repo = document_repo

    async def execute(
        self,
        author_id: int,
        stage_id: int | None = None,
        roles: list[Literal['author', 'reviewer']] | None = None,
        review_statuses: list[Literal['accepted', 'declined']] | None = None,
        categories: list[str] | None = None,
        doc_statuses: list[Literal['new_comment', 'not_viewed', 'viewed', 'waiting', 'action_required', 'sent']] | None = None,
        ) -> list[Document]:
        return self._document_repo.get_document_with_filters(
            author_id,
            stage_id,
            roles,
            review_statuses,
            categories,
            doc_statuses,
            )