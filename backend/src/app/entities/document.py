from dataclasses import dataclass

from entities import User


@dataclass(frozen=True, slots=True)
class Document:
    title: str
    file: str
    authors: list[int]
    pdf_file: str | None = None
