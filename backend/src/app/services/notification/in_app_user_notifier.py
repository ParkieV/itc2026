import copy
import logging

from repositories.inmemory_user_notifications_repo import InMemoryUserNotificationsRepository
from services.notification.event import NotificationEvent

logger = logging.getLogger(__name__)


class InAppUserNotifier:
    """Записывает одно и то же событие в in-app хранилище для каждого user_id из event.user_ids."""

    def __init__(self, repo: InMemoryUserNotificationsRepository) -> None:
        self._repo = repo

    async def notify(self, event: NotificationEvent) -> None:
        if not event.user_ids:
            return
        payload = copy.deepcopy(event.payload)
        for uid in event.user_ids:
            try:
                await self._repo.add(
                    user_id=uid,
                    event_type=event.event_type,
                    title=event.subject,
                    body=event.body,
                    payload=payload,
                )
            except Exception:
                logger.exception(
                    "In-app user notification failed",
                    extra={"user_id": uid, "event_type": event.event_type},
                )
