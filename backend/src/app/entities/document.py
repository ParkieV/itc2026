from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Document:
    title: str
    description: str
    file_id: int | None = None
    authors: list[int]
    stage_id: int
    created_at: int | None = None
    modified_at: int | None = None
    pdf_file_id: int | None = None
