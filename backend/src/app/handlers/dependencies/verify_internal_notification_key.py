from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Header, HTTPException, status

from config import AppConfig


@inject
async def verify_internal_notification_key(
    app_config: FromDishka[AppConfig],
    x_internal_notification_key: Annotated[str | None, Header(alias="X-Internal-Notification-Key")] = None,
) -> None:
    configured = app_config.internal_notification_api_key
    if app_config.is_dev() and not configured:
        return
    if not configured or x_internal_notification_key != configured:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
