from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Review:
    stage_id: int
    doc_id: int
    user_id: int
    is_aproved: bool
    is_viewed: bool
