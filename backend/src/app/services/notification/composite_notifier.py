import logging

from services.notification.event import NotificationEvent
from services.notification.protocol import Notifier

logger = logging.getLogger(__name__)


class CompositeNotifier:
    def __init__(self, *channels: Notifier) -> None:
        self._channels = channels

    async def notify(self, event: NotificationEvent) -> None:
        for channel in self._channels:
            try:
                await channel.notify(event)
            except Exception:
                logger.exception(
                    "Notification channel raised",
                    extra={"channel": type(channel).__name__},
                )
