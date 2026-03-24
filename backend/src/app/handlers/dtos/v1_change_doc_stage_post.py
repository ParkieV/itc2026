from pydantic import BaseModel, Field


class V1ChangeDocStagePostRequest(BaseModel):
    doc_id: int
    stage_id: int


class V1_CHANGE_DOC_STAGE_POST_RESPONSE200(BaseModel):
    """Стадия документа успешно изменена."""


class V1_CHANGE_DOC_STAGE_POST_RESPONSE400(BaseModel):
    """Некорректный переход: не тот next_stage, совпадение этапа, отклонение ревью или не все ACCEPTED."""

    detail: str = Field(description="Текст ошибки")


class V1_CHANGE_DOC_STAGE_POST_RESPONSE404(BaseModel):
    """Документ или стадия не найдены."""

    detail: str = Field(description="Текст ошибки")
