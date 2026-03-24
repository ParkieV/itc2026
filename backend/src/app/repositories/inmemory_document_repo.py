from dataclasses import asdict
from datetime import datetime
from zoneinfo import ZoneInfo

from entities import Document


class InMemoryDocumentRepository:
    @staticmethod
    def _now_msk_timestamp() -> int:
        return int(datetime.now(ZoneInfo("Europe/Moscow")).timestamp())

    def __init__(self) -> None:
        now_ts = self._now_msk_timestamp()
        self._docs = {
            '1': {
                "title": "test",
                "description": "test description 1",
                "file": "test",
                "pdf_file": "test",
                "authors": [1],
                "stage_id": 1,
                "created_at": now_ts,
                "modified_at": now_ts,
            },
            '2': {
                "title": "test",
                "description": "test description 2",
                "file": "test",
                "pdf_file": "test",
                "authors": [1],
                "stage_id": 2,
                "created_at": now_ts,
                "modified_at": now_ts,
            },
            '3': {
                "title": "test",
                "description": "test description 3",
                "file": "test",
                "pdf_file": "test",
                "authors": [2],
                "stage_id": 2,
                "created_at": now_ts,
                "modified_at": now_ts,
            },
        }
        self._count = 2

    def _add_count(self) -> None:
        self._count += 1

    def add_document(self, document: Document) -> None:
        created_at = document.created_at or self._now_msk_timestamp()
        modified_at = document.modified_at or created_at
        document_to_store = Document(
            title=document.title,
            description=document.description,
            file=document.file,
            authors=document.authors,
            stage_id=document.stage_id,
            created_at=created_at,
            modified_at=modified_at,
            pdf_file=document.pdf_file,
        )
        self._docs[self._count] = asdict(document_to_store)
        self._add_count()

    def get_document(self, document_id: int) -> Document | None:
        document_model = self._docs.get(str(document_id))

        if document_model is None:
            return None

        return Document(
            title=document_model['title'],
            description=document_model['description'],
            file=document_model['file'],
            pdf_file=document_model['pdf_file'],
            authors=document_model['authors'],
            stage_id=document_model['stage_id'],
            created_at=document_model['created_at'],
            modified_at=document_model['modified_at'],
        )

    def get_list(self) -> list[Document]:
        out: list[Document] = []
        for document_model in self._docs.values():
            out.append(
                Document(
                    title=document_model['title'],
                    description=document_model['description'],
                    file=document_model['file'],
                    pdf_file=document_model['pdf_file'],
                    authors=document_model['authors'],
                    stage_id=document_model['stage_id'],
                    created_at=document_model['created_at'],
                    modified_at=document_model['modified_at'],
                )
            )
        return out

    def patch_document(self, document: Document, document_id: int) -> str:
        existing = self._docs.get(str(document_id))
        if existing is None:
            raise ValueError(f'Document with id {document_id} does not exist')

        patched = Document(
            title=document.title,
            description=document.description,
            file=document.file,
            authors=document.authors,
            stage_id=document.stage_id,
            created_at=existing['created_at'],
            modified_at=self._now_msk_timestamp(),
            pdf_file=document.pdf_file,
        )
        self._docs[str(document_id)] = asdict(patched)
