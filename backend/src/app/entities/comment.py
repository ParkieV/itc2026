from dataclasses import dataclass

from entities.comment_status import CommentStatus


@dataclass(frozen=True, slots=True)
class Comment:
    comment_id: int
    doc_id: int
    stage_id: int
    user_id: int
    subject: str
    content: str
    xfdf: str
    created_at: int
    reply_to: int | None = None
    status: CommentStatus | None = None
    is_viewed: bool = False
