from dataclasses import dataclass

from entities.review_status import ReviewStatus


@dataclass(frozen=True, slots=True)
class Review:
    stage_id: int
    doc_id: int
    user_id: int
    is_viewed: bool
    status: ReviewStatus | None = None
