from pydantic import BaseModel, Field, RootModel

from entities.comment_status import CommentStatus


class V1CabinetDocumentCreateCommentRequest(BaseModel):
    stage_id: int
    subject: str
    content: str
    xfdf: str
    reply_to: int | None = None


class V1_CABINET_DOCUMENT_COMMENTS_POST_RESPONSE200(BaseModel):
    """Комментарий успешно создан."""


class V1_CABINET_DOCUMENT_COMMENTS_POST_RESPONSE401(BaseModel):
    """Невалидный, просроченный или отсутствующий токен."""

    detail: str = Field(description="Текст ошибки")


class V1_CABINET_DOCUMENT_COMMENTS_POST_RESPONSE404(BaseModel):
    """Документ, этап или пользователь не найден."""

    detail: str = Field(description="Текст ошибки")
