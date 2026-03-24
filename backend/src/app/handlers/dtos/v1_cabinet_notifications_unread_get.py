from typing import Any

from pydantic import BaseModel, Field


class V1CabinetNotificationUnreadItem(BaseModel):
    id: int
    event_type: str
    title: str
    body: str
    payload: dict[str, Any]
    created_at: int = Field(description="Unix timestamp (Europe/Moscow при создании записи)")


class V1CabinetNotificationsUnreadGetResponse(BaseModel):
    items: list[V1CabinetNotificationUnreadItem]


class V1_CABINET_NOTIFICATIONS_UNREAD_GET_RESPONSE200(V1CabinetNotificationsUnreadGetResponse):
    """Список непрочитанных уведомлений текущего пользователя (JWT sub)."""


class V1_CABINET_NOTIFICATIONS_UNREAD_GET_RESPONSE401(BaseModel):
    """Невалидный JWT."""

    detail: str = Field(description="Текст ошибки")
