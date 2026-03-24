from typing import Any

from pydantic import BaseModel, Field


class V1UserNotificationsPostRequest(BaseModel):
    user_id: int = Field(description="Получатель in-app уведомления")
    event_type: str = Field(description="Тип события, например review.assigned")
    title: str
    body: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class V1UserNotificationsPostResponse(BaseModel):
    notification_id: int


class V1_USER_NOTIFICATIONS_POST_RESPONSE200(V1UserNotificationsPostResponse):
    """Уведомление создано."""


class V1_USER_NOTIFICATIONS_POST_RESPONSE403(BaseModel):
    """Неверный или отсутствующий X-Internal-Notification-Key (в prod или при заданном ключе)."""

    detail: str = Field(description="Текст ошибки")


class V1_USER_NOTIFICATIONS_POST_RESPONSE404(BaseModel):
    """Пользователь user_id не найден."""

    detail: str = Field(description="Текст ошибки")
