from dataclasses import dataclass

from entities.document import Document
from entities.stage import Stage
from entities.user import User


@dataclass(frozen=True, slots=True)
class StageWithReviewerAndDocs:
    stage: Stage
    docs: list[Document]
    reviewers: list[User]
