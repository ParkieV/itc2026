from pydantic import BaseModel, Field

from entities.comment_status import CommentStatus

from .comment_author_preview import CommentAuthorPreview


class V1CabinetDocumentsCommentPatchResponse(BaseModel):
    comment_id: int
    doc_id: int
    stage_id: int
    author: CommentAuthorPreview
    reply_to: int | None = None
    remark: str | None = None
    proposal: str | None = None
    justification: str | None = None
    developer_response: str | None = None
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
