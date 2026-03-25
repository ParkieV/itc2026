from dataclasses import asdict
from typing import Literal

from entities import Document
from utils.datetime_iso import now_iso_msk


class InMemoryDocumentRepository:
    def __init__(self) -> None:
        now_iso = now_iso_msk()
        # Similar structure to `InMemoryDocumentFilesRepository`:
        # store documents in a dict keyed by `doc_id` and keep `_count` in sync.
        self._docs_by_doc_id = {
            1: {
                "title": "test",
                "description": "test description 1",
                "file_id": 1,
                "pdf_file_id": 1,
                "authors": [1],
                "stage_id": 1,
                "created_at": now_iso,
                "modified_at": now_iso,
            },
            2: {
                "title": "test",
                "description": "test description 2",
                "file_id": 1,
                "pdf_file_id": 1,
                "authors": [1],
                "stage_id": 2,
                "created_at": now_iso,
                "modified_at": now_iso,
            },
            3: {
                "title": "test",
                "description": "test description 3",
                "file_id": 1,
                "pdf_file_id": 1,
                "authors": [2],
                "stage_id": 2,
                "created_at": now_iso,
                "modified_at": now_iso,
            },
        }
        self._count = len(self._docs_by_doc_id.keys()) + 1

    def _add_count(self) -> None:
        self._count += 1

    def get_next_document_id(self) -> int:
        return self._count

    def add_document(self, document: Document) -> None:
        created_at = document.created_at or now_iso_msk()
        modified_at = document.modified_at or created_at

        self._docs_by_doc_id[self._count] = {
            **asdict(document),
            "created_at": created_at,
            "modified_at": modified_at,
        }
        self._add_count()

    def get_document(self, document_id: int) -> Document | None:
        document_model = self._docs_by_doc_id.get(document_id)

        if document_model is None:
            return None

        return Document(
            title=document_model['title'],
            description=document_model['description'],
            file_id=document_model['file_id'],
            pdf_file_id=document_model.get('pdf_file_id'),
            authors=document_model['authors'],
            stage_id=document_model['stage_id'],
            created_at=document_model['created_at'],
            modified_at=document_model['modified_at'],
            doc_id=document_id,
        )

    def get_list(self) -> list[Document]:
        out: list[Document] = []
        for doc_id, document_model in self._docs_by_doc_id.items():
            out.append(
                Document(
                    title=document_model['title'],
                    description=document_model['description'],
                    file_id=document_model['file_id'],
                    pdf_file_id=document_model['pdf_file_id'],
                    authors=document_model['authors'],
                    stage_id=document_model['stage_id'],
                    created_at=document_model['created_at'],
                    modified_at=document_model['modified_at'],
                    doc_id=doc_id,
                )
            )
        return out

    def patch_document(self, document: Document, document_id: int) -> str:
        existing = self._docs_by_doc_id.get(document_id)
        if existing is None:
            raise ValueError(f'Document with id {document_id} does not exist')

        patched = Document(
            title=document.title,
            description=document.description,
            file_id=document.file_id,
            authors=document.authors,
            stage_id=document.stage_id,
            created_at=existing['created_at'],
            modified_at=now_iso_msk(),
            pdf_file_id=document.pdf_file_id,
            doc_id=document_id,
        )
        self._docs_by_doc_id[document_id] = asdict(patched)
        return str(document_id)

    def get_document_with_filters(
        self,
        author_id: int,
        stage_id: int | None = None,
        roles: list[Literal['author', 'reviewer']] | None = None,
        review_statuses: list[Literal['accepted', 'declined']] | None = None,
        categories: list[str] | None = None,
        doc_statuses: list[Literal['new_comment', 'not_viewed', 'viewed', 'waiting', 'action_required', 'sent']] | None = None,
        ) -> list[Document]:
        filtered = self._docs_by_doc_id.items()
        if stage_id is not None:
            filtered = [(doc_id, doc) for doc_id, doc in filtered if doc['stage_id'] == stage_id]
        if roles is not None:
            if 'author' in roles:
                filtered = [(doc_id, doc) for doc_id, doc in filtered if author_id in doc['authors']]
        if review_statuses is not None:
            filtered = [(doc_id, doc) for doc_id, doc in filtered if doc['review_status'] in review_statuses]
        if categories is not None:
            filtered = [(doc_id, doc) for doc_id, doc in filtered if doc['categories'] in categories]
        if doc_statuses is not None:
            filtered = [(doc_id, doc) for doc_id, doc in filtered if doc['doc_status'] in doc_statuses]
        return [
            Document(
                title=document_model['title'],
                description=document_model['description'],
                file_id=document_model['file_id'],
                pdf_file_id=document_model['pdf_file_id'],
                authors=document_model['authors'],
                stage_id=document_model['stage_id'],
                created_at=document_model['created_at'],
                modified_at=document_model['modified_at'],
                doc_id=doc_id,
            )
            for doc_id, document_model in filtered
        ]