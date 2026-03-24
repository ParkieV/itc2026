from pydantic import BaseModel, Field


class V1ChangeDocStagePostRequest(BaseModel):
    doc_id: int
    stage_id: int


class V1_CHANGE_DOC_STAGE_POST_RESPONSE200(BaseModel):
    """Стадия документа успешно изменена."""


class V1_CHANGE_DOC_STAGE_POST_RESPONSE400(BaseModel):
    """Целевая стадия указана некорректно (например, совпадает с текущей)."""

    detail: str = Field(description="Текст ошибки")


class V1_CHANGE_DOC_STAGE_POST_RESPONSE404(BaseModel):
    """Документ или стадия не найдены."""

    detail: str = Field(description="Текст ошибки")
