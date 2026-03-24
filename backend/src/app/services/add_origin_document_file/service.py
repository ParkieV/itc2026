from pathlib import Path
from typing import BinaryIO, Protocol

from entities import Document
from repositories.inmemory_document_files_repo import InMemoryDocumentFilesRepository
from services.add_origin_document_file.exceptions import FileExists, InvalidDocumentFormat

ALLOWED_DOCUMENT_SUFFIXES = {".docx", ".pdf"}
ORIGINS_DIR = Path("src/static/origins")


class UploadedFileLike(Protocol):
    filename: str | None
    file: BinaryIO


class AddOriginDocumentFileService:
    def __init__(self, document_files_repo: InMemoryDocumentFilesRepository):
        self._document_files_repo = document_files_repo

    async def execute(self, document: Document, upload_file: UploadedFileLike) -> tuple[int, str]:
        file_name = upload_file.filename or ""
        if not file_name:
            raise InvalidDocumentFormat("Filename is required")

        suffix = Path(file_name).suffix.lower()
        if suffix not in ALLOWED_DOCUMENT_SUFFIXES:
            raise InvalidDocumentFormat("Only .docx and .pdf are supported")

        if self._document_files_repo.file_exists(file_name, ORIGINS_DIR):
            raise FileExists(f"File with name '{file_name}' already exists")

        file_id = self._document_files_repo.get_next_file_id()
        saved_origin_path = self._document_files_repo.save_uploaded_file(upload_file, ORIGINS_DIR)
        self._document_files_repo.upsert_paths(
            file_id=file_id,
            origin_file_path=saved_origin_path,
            pdf_file_path=None,
        )
        return file_id, saved_origin_path
