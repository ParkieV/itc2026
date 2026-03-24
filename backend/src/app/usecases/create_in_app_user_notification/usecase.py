from typing import Any

from services.user_in_app_notification.service import UserInAppNotificationService


class CreateInAppUserNotificationUseCase:
    def __init__(self, notification_service: UserInAppNotificationService) -> None:
        self._notification_service = notification_service

    async def execute(
        self,
        user_id: int,
        event_type: str,
        title: str,
        body: str,
        payload: dict[str, Any],
    ) -> int:
        return await self._notification_service.add_for_user(
            user_id=user_id,
            event_type=event_type,
            title=title,
            body=body,
            payload=payload,
        )
