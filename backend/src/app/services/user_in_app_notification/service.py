from typing import Any

from entities.user_notification import UserNotification
from repositories.inmemory_user_notifications_repo import InMemoryUserNotificationsRepository
from services.get_user.service import GetUserService
from services.user_in_app_notification.exceptions import UserNotificationNotFound


class UserInAppNotificationService:
    def __init__(
        self,
        repo: InMemoryUserNotificationsRepository,
        get_user_service: GetUserService,
    ) -> None:
        self._repo = repo
        self._get_user_service = get_user_service

    async def add_for_user(
        self,
        user_id: int,
        event_type: str,
        title: str,
        body: str,
        payload: dict[str, Any],
    ) -> int:
        await self._get_user_service.execute(user_id)
        return await self._repo.add(
            user_id=user_id,
            event_type=event_type,
            title=title,
            body=body,
            payload=payload,
        )

    async def list_unread(self, user_id: int) -> list[UserNotification]:
        return await self._repo.list_unread_for_user(user_id)

    async def mark_read(self, notification_id: int, user_id: int) -> None:
        ok = await self._repo.mark_read(notification_id, user_id)
        if not ok:
            raise UserNotificationNotFound()
