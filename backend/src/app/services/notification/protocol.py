from typing import Protocol

from services.notification.event import NotificationEvent


class Notifier(Protocol):
    async def notify(self, event: NotificationEvent) -> None: ...
