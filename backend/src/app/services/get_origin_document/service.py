from entities import Document
from repositories.inmemory_document_files_repo import InMemoryDocumentFilesRepository
from repositories.inmemory_document_repo import InMemoryDocumentRepository
from services.get_origin_document.exceptions import DocumentNotFound, DocumentNotAllowed


class GetOriginDocumentService:
    def __init__(
            self,
            document_repo: InMemoryDocumentRepository,
            document_files_repo: InMemoryDocumentFilesRepository,
    ):
        self._document_repo = document_repo
        self._document_files_repo = document_files_repo

    async def execute(self, document_id: int, client_id: int) -> Document:
        if (document := self._document_repo.get_document(document_id)) is None:
            raise DocumentNotFound(f"Document with id {document_id} not found")

        if client_id not in document.authors:
            raise DocumentNotAllowed(f"Client with id {client_id} is not allowed to access document with id {document_id}")

        if document.file_id is None:
            return document

        if (paths := self._document_files_repo.get_paths(document.file_id)) is None:
            return document

        return Document(
            title=document.title,
            description=document.description,
            authors=document.authors,
            stage_id=document.stage_id,
            file_id=document.file_id,
            pdf_file_id=document.pdf_file_id,
            created_at=document.created_at,
            modified_at=document.modified_at,
            doc_id=document_id,
        )
