from dataclasses import dataclass

from entities.document import Document
from entities.review import Review


@dataclass(frozen=True, slots=True)
class DocumentDetail:
    document: Document
    reviews: list[Review]
