import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from config import NotificationSettings
from services.notification.event import NotificationEvent

logger = logging.getLogger(__name__)


class WebhookNotifier:
    def __init__(self, settings: NotificationSettings) -> None:
        self._settings = settings

    async def notify(self, event: NotificationEvent) -> None:
        url = self._settings.webhook_url
        if not url or not url.strip():
            return

        body: dict[str, Any] = {
            "event_type": event.event_type,
            "subject": event.subject,
            "body": event.body,
            "payload": event.payload,
            "sent_at": datetime.now(UTC).isoformat(),
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.post(url, json=body)
                r.raise_for_status()
        except httpx.HTTPError:
            logger.exception("Webhook notification failed")
