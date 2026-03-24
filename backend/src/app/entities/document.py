from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Document:
    title: str
    description: str
    authors: list[int]
    stage_id: int
    file_id: int | None = None
    created_at: int | None = None
    modified_at: int | None = None
    pdf_file_id: int | None = None
