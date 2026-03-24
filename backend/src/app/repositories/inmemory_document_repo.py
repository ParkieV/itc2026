from dataclasses import asdict

from entities import Document


class InMemoryDocumentRepository:
    def __init__(self) -> None:
        self._docs = {
            '1': {
                "title": "test",
                "authors": [1],
                "file_id": 1,
                "pdf_file_id": 1,
            }
        }
        self._count = 2

    def _add_count(self) -> None:
        self._count += 1

    def get_next_document_id(self) -> int:
        return self._count

    def add_document(self, document: Document) -> None:
        self._docs[str(self._count)] = asdict(document)
        self._add_count()

    def get_document(self, document_id: int) -> Document | None:
        document_model = self._docs.get(str(document_id))

        if document_model is None:
            return None

        return Document(
            title=document_model['title'],
            authors=document_model['authors'],
            file_id=document_model['file_id'],
            pdf_file_id=document_model.get('pdf_file_id'),
        )

    def patch_document(self, document: Document, document_id: int) -> str:
        if self._docs.get(str(document_id)) is None:
            raise ValueError(f'Document with id {document_id} does not exist')

        self._docs[str(document_id)] = asdict(document)
