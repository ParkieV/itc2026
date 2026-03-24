from pydantic import BaseModel, Field

from entities.comment_status import CommentStatus

from .v1_cabinett_document_comments import V1CabinettDocumentCommentResponse


class V1CabinetDocumentsCommentPatchRequest(BaseModel):
    """Поля со значением null/отсутствуют — не обновляются."""

    is_viewed: bool | None = None
    status: CommentStatus | None = None


class V1_CABINET_DOCUMENTS_COMMENT_PATCH_RESPONSE200(V1CabinettDocumentCommentResponse):
    """Обновлённый комментарий."""


class V1_CABINET_DOCUMENTS_COMMENT_PATCH_RESPONSE401(BaseModel):
    """Невалидный, просроченный или отсутствующий токен."""

    detail: str = Field(description="Текст ошибки")


class V1_CABINET_DOCUMENTS_COMMENT_PATCH_RESPONSE404(BaseModel):
    """Документ или комментарий не найден."""

    detail: str = Field(description="Текст ошибки")
