from dataclasses import dataclass
from typing import Any

from entities.stage import Stage
from entities.user import User


@dataclass(frozen=True, slots=True)
class StageWithReviewerAndDocs:
    stage: Stage
    docs: list[Any]
    reviewers: list[User]
