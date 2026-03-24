from pydantic import BaseModel, Field

from handlers.dtos.v1_cabinett_document_comments import V1CabinettDocumentCommentResponse


class V1CabinetDocumentGetDocumentResponse(BaseModel):
    title: str
    description: str
    file: str
    authors: list[int]
    stage_id: int
    created_at: str
    modified_at: str
    pdf_file: str | None = None


class V1CabinetDocumentGetReviewResponse(BaseModel):
    stage_id: int
    doc_id: int
    user_id: int
    is_aproved: bool
    is_viewed: bool


class V1CabinetDocumentGetResponse(BaseModel):
    document: V1CabinetDocumentGetDocumentResponse
    reviews: list[V1CabinetDocumentGetReviewResponse]
    comments: list[V1CabinettDocumentCommentResponse] = Field(
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
