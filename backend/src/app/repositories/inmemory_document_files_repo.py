from pathlib import Path
import shutil
from typing import BinaryIO, Protocol


class UploadedFileLike(Protocol):
    filename: str | None
    file: BinaryIO


class InMemoryDocumentFilesRepository:
    def __init__(self) -> None:
        self._paths_by_file_id: dict[int, dict[str, str | None]] = {
            1: {
                "origin_file_path": "src/static/origins/test.docx",
                "pdf_file_path": "src/static/pdfs/test.pdf",
            },
            2: {
                "origin_file_path": "src/static/origins/test2.docx",
                "pdf_file_path": "src/static/pdfs/test2.pdf",
            },
            3: {
                "origin_file_path": "src/static/origins/test3.docx",
                "pdf_file_path": "src/static/pdfs/test3.pdf",
            },
        }
        self._count = len(self._paths_by_file_id.keys()) + 1

    def get_next_file_id(self) -> int:
        return self._count

    def _add_count(self) -> None:
        self._count += 1

    def file_exists(self, filename: str, target_dir: Path) -> bool:
        return (target_dir / filename).exists()

    def save_uploaded_file(self, upload_file: UploadedFileLike, target_dir: Path) -> str:
        target_dir.mkdir(parents=True, exist_ok=True)
        destination = target_dir / (upload_file.filename or "")
        upload_file.file.seek(0)
        with destination.open("wb") as destination_file:
            shutil.copyfileobj(upload_file.file, destination_file)
        return str(destination)

    def copy_file(
        self,
        source_path: str | Path,
        target_dir: Path,
        target_filename: str | None = None,
    ) -> str:
        source = Path(source_path)
        target_dir.mkdir(parents=True, exist_ok=True)
        destination = target_dir / (target_filename or source.name)
        shutil.copy2(source, destination)
        return str(destination)

    def upsert_paths(
        self,
        file_id: int,
        origin_file_path: str | None = None,
        pdf_file_path: str | None = None,
    ) -> None:
        current = self._paths_by_file_id.get(
            file_id,
            {"origin_file_path": None, "pdf_file_path": None},
        )
        if origin_file_path is not None:
            current["origin_file_path"] = origin_file_path
        if pdf_file_path is not None:
            current["pdf_file_path"] = pdf_file_path
        self._paths_by_file_id[file_id] = current
        if file_id >= self._count:
            self._add_count()

    def get_paths(self, file_id: int) -> dict[str, str | None] | None:
        return self._paths_by_file_id.get(file_id)
