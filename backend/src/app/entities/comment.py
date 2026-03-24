from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Comment:
    doc_id: int
    stage_id: int
    user_id: int
    subject: str
    content: str
    created_at: int
