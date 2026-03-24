from pydantic import BaseModel, Field, RootModel


class V1CabinettDocumentCommentResponse(BaseModel):
    doc_id: int
    stage_id: int
    user_id: int
    subject: str
    content: str
    created_at: str


class V1CabinettDocumentCreateCommentRequest(BaseModel):
    stage_id: int
    subject: str
    content: str


class V1_CABINETT_DOCUMENT_COMMENTS_POST_RESPONSE200(BaseModel):
    """Комментарий успешно создан."""


class V1_CABINETT_DOCUMENT_COMMENTS_GET_RESPONSE200(
    RootModel[list[V1CabinettDocumentCommentResponse]]
):
    """Список комментариев документа."""


class V1_CABINETT_DOCUMENT_COMMENTS_RESPONSE401(BaseModel):
    """Невалидный, просроченный или отсутствующий токен."""

    detail: str = Field(description="Текст ошибки")


class V1_CABINETT_DOCUMENT_COMMENTS_RESPONSE404(BaseModel):
    """Документ, этап или пользователь не найден."""

    detail: str = Field(description="Текст ошибки")
