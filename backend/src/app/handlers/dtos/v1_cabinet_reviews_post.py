from pydantic import BaseModel, Field

from entities.review_status import ReviewStatus


class V1CabinetReviewsUpdateRequest(BaseModel):
    doc_id: int
    stage_id: int


class V1CabinetReviewsStatusRequest(BaseModel):
    doc_id: int
    stage_id: int
    status: ReviewStatus


class V1CabinetReviewsCreateRequest(BaseModel):
    doc_id: int
    user_id: int
    stage_id: int


class V1_CABINET_REVIEWS_VIEW_POST_RESPONSE200(BaseModel):
    """Статус просмотра ревью успешно обновлен."""


class V1_CABINET_REVIEWS_STATUS_POST_RESPONSE200(BaseModel):
    """Статус ревью успешно обновлён."""


class V1_CABINET_REVIEWS_POST_RESPONSE200(BaseModel):
    """Ревью успешно создано."""


class V1_CABINET_REVIEWS_POST_RESPONSE401(BaseModel):
    """Невалидный, просроченный или отсутствующий токен."""

    detail: str = Field(description="Текст ошибки")


class V1_CABINET_REVIEWS_POST_RESPONSE400(BaseModel):
    """Нарушена уникальность review (doc_id, user_id, stage_id)."""

    detail: str = Field(description="Текст ошибки")


class V1_CABINET_REVIEWS_POST_RESPONSE404(BaseModel):
    """Пользователь, этап или документ не найден."""

    detail: str = Field(description="Текст ошибки")
