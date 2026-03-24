from pydantic import BaseModel, Field

from entities.comment_status import CommentStatus


class V1CabinetDocumentsCommentPatchResponse(BaseModel):
    comment_id: int
    doc_id: int
    stage_id: int
    user_id: int
    reply_to: int | None = None
    subject: str
    content: str
    xfdf: str
    status: CommentStatus | None = None
    is_viewed: bool = False
    created_at: str


class V1CabinetDocumentsCommentPatchRequest(BaseModel):
    """Поля со значением null/отсутствуют — не обновляются."""

    is_viewed: bool | None = None
    status: CommentStatus | None = None


class V1_CABINET_DOCUMENTS_COMMENT_PATCH_RESPONSE200(V1CabinetDocumentsCommentPatchResponse):
    """Обновлённый комментарий."""


class V1_CABINET_DOCUMENTS_COMMENT_PATCH_RESPONSE401(BaseModel):
    """Невалидный, просроченный или отсутствующий токен."""

    detail: str = Field(description="Текст ошибки")


class V1_CABINET_DOCUMENTS_COMMENT_PATCH_RESPONSE404(BaseModel):
    """Документ или комментарий не найден."""

    detail: str = Field(description="Текст ошибки")
