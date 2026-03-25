from pydantic import BaseModel, Field

from entities.document_user_status import DocumentUserStatus
from entities.review_status import ReviewStatus

from handlers.dtos.v1_cabinet_document_comments_get import V1CabinetDocumentCommentResponse


class V1CabinetDocumentGetDocumentResponse(BaseModel):
    title: str
    description: str
    file_id: int
    authors: list[int]
    stage_id: int
    created_at: str
    modified_at: str
    pdf_file_id: int | None = None
    status: DocumentUserStatus | None = Field(
        default=None,
        description="Статус документа для текущего пользователя (автор или ревьюер); иначе null.",
    )


class V1CabinetDocumentGetReviewResponse(BaseModel):
    stage_id: int
    doc_id: int
    user_id: int
    status: ReviewStatus | None = None
    is_viewed: bool


class V1CabinetDocumentGetResponse(BaseModel):
    document: V1CabinetDocumentGetDocumentResponse
    reviews: list[V1CabinetDocumentGetReviewResponse]
    comments: list[V1CabinetDocumentCommentResponse] = Field(
        description="Комментарии к документу на текущем этапе (doc_id и stage_id документа).",
    )


class V1_CABINET_DOCUMENT_GET_RESPONSE200(V1CabinetDocumentGetResponse):
    """Информация о документе, ревью и комментариях на текущем этапе."""


class V1_CABINET_DOCUMENT_GET_RESPONSE401(BaseModel):
    """Невалидный, просроченный или отсутствующий токен."""

    detail: str = Field(description="Текст ошибки")


class V1_CABINET_DOCUMENT_GET_RESPONSE404(BaseModel):
    """Документ не найден."""

    detail: str = Field(description="Текст ошибки")
