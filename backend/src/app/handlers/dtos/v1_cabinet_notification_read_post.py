from pydantic import BaseModel, Field

from handlers.dtos.helper import OpenApiNoContent


class V1_CABINET_NOTIFICATION_READ_POST_RESPONSE204(OpenApiNoContent):
    """Уведомление отмечено прочитанным."""


class V1_CABINET_NOTIFICATION_READ_POST_RESPONSE401(BaseModel):
    """Невалидный JWT."""

    detail: str = Field(description="Текст ошибки")


class V1_CABINET_NOTIFICATION_READ_POST_RESPONSE404(BaseModel):
    """Нет такого уведомления или оно принадлежит другому пользователю."""

    detail: str = Field(description="Текст ошибки")
