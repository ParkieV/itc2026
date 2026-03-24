from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Stage:
    stage_id: int
    next_stage: int
    title: str
