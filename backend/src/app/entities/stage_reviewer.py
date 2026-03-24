from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StageReviewer:
    reviewer_id: int
    stage_id: int
