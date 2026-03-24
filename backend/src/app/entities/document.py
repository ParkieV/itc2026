from dataclasses import dataclass

from entities import User


@dataclass(frozen=True, slots=True)
class Document:
    title: str
    authors: list[int]
    file_id: int | None = None
    pdf_file_id: int | None = None
