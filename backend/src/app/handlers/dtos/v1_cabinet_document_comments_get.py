from pydantic import BaseModel, Field, RootModel

from entities.comment_status import CommentStatus

from .comment_author_preview import CommentAuthorPreview


class V1CabinetDocumentCommentResponse(BaseModel):
    comment_id: int
    doc_id: int
    stage_id: int
    author: CommentAuthorPreview
    reply_to: int | None = None
    subject: str
    content: str
    xfdf: str
    status: CommentStatus | None = None
    is_viewed: bool = False
    created_at: str

class V1_CABINET_DOCUMENT_COMMENTS_GET_RESPONSE200(
    RootModel[list[V1CabinetDocumentCommentResponse]]
):
    """Список комментариев документа."""


class V1_CABINET_DOCUMENT_COMMENTS_GET_RESPONSE401(BaseModel):
    """Невалидный, просроченный или отсутствующий токен."""

    detail: str = Field(description="Текст ошибки")


class V1_CABINET_DOCUMENT_COMMENTS_GET_RESPONSE404(BaseModel):
    """Документ, этап или пользователь не найден."""

    detail: str = Field(description="Текст ошибки")
