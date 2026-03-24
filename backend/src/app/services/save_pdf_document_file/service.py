from pathlib import Path
import tempfile

from docx2pdf import convert

from entities import Document
from repositories.inmemory_document_files_repo import InMemoryDocumentFilesRepository
from services.save_pdf_document_file.exceptions import (
    OriginFileNotFound,
    PdfConversionFailed,
    PdfFileExists,
    UnsupportedOriginFormat,
)

PDFS_DIR = Path("src/static/pdfs")
ALLOWED_ORIGIN_SUFFIXES = {".pdf", ".docx"}


class SavePdfDocumentFileService:
    def __init__(self, document_files_repo: InMemoryDocumentFilesRepository):
        self._document_files_repo = document_files_repo

    async def execute(self, file_id: int, document: Document, origin_file_path: str) -> int:
        origin_path = Path(origin_file_path)
        if not origin_path.is_file():
            raise OriginFileNotFound(f"Origin file does not exist: {origin_path}")

        suffix = origin_path.suffix.lower()
        if suffix not in ALLOWED_ORIGIN_SUFFIXES:
            raise UnsupportedOriginFormat("Only .pdf and .docx origin files are supported")

        target_pdf_name = f"{origin_path.stem}.pdf"
        if self._document_files_repo.file_exists(target_pdf_name, PDFS_DIR):
            raise PdfFileExists(f"PDF with name '{target_pdf_name}' already exists")

        if suffix == ".pdf":
            saved_pdf_path = self._document_files_repo.copy_file(
                source_path=origin_path,
                target_dir=PDFS_DIR,
                target_filename=target_pdf_name,
            )
        else:
            converted_pdf_path = self._convert_docx_to_pdf(origin_path)
            try:
                saved_pdf_path = self._document_files_repo.copy_file(
                    source_path=converted_pdf_path,
                    target_dir=PDFS_DIR,
                    target_filename=target_pdf_name,
                )
            finally:
                converted_pdf_path.unlink(missing_ok=True)

        self._document_files_repo.upsert_paths(
            file_id=file_id,
            origin_file_path=str(origin_path),
            pdf_file_path=saved_pdf_path,
        )
        return file_id

    def _convert_docx_to_pdf(self, origin_path: Path) -> Path:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            try:
                convert(str(origin_path), str(output_dir))
            except Exception as err:  # noqa: BLE001
                raise PdfConversionFailed(f"Failed converting docx to pdf: {err}") from err

            converted = output_dir / f"{origin_path.stem}.pdf"
            if not converted.is_file():
                raise PdfConversionFailed("Converted PDF file was not created")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                temp_pdf.write(converted.read_bytes())
                return Path(temp_pdf.name)
