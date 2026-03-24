from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Document:
    title: str
    description: str
    file: str
    authors: list[int]
    stage_id: int
    created_at: str | None = None
    modified_at: str | None = None
    pdf_file: str | None = None
