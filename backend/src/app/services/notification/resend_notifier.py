import logging

import httpx

from config import NotificationSettings
from services.get_user.exceptions import UserNotFound
from services.get_user.service import GetUserService
from services.notification.event import NotificationEvent

logger = logging.getLogger(__name__)

_RESEND_URL = "https://api.resend.com/emails"


class ResendEmailNotifier:
    """Если в событии заданы user_ids — письмо уходит на email каждого пользователя из профиля. Иначе — на NOTIFY_JUDGE_EMAILS."""

    def __init__(self, settings: NotificationSettings, get_user_service: GetUserService) -> None:
        self._settings = settings
        self._get_user_service = get_user_service

    def _judge_recipients(self) -> list[str]:
        raw = self._settings.judge_emails.strip()
        if not raw:
            return []
        return [e.strip() for e in raw.split(",") if e.strip()]

    async def _post(
        self,
        client: httpx.AsyncClient,
        api_key: str,
        mail_from: str,
        to: list[str],
        subject: str,
        body: str,
    ) -> None:
        r = await client.post(
            _RESEND_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": mail_from,
                "to": to,
                "subject": subject,
                "text": body,
            },
        )
        r.raise_for_status()

    async def notify(self, event: NotificationEvent) -> None:
        key = self._settings.resend_api_key
        mail_from = self._settings.mail_from
        if not key or not mail_from:
            return

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                if event.user_ids:
                    for uid in event.user_ids:
                        try:
                            user = await self._get_user_service.execute(uid)
                        except UserNotFound:
                            logger.warning("Resend: пользователь user_id=%s не найден, пропуск", uid)
                            continue
                        email = (user.email or "").strip()
                        if not email:
                            logger.warning("Resend: у user_id=%s пустой email, пропуск", uid)
                            continue
                        try:
                            await self._post(client, key, mail_from, [email], event.subject, event.body)
                        except httpx.HTTPError:
                            logger.exception("Resend: ошибка отправки на %s (user_id=%s)", email, uid)
                    return

                to = self._judge_recipients()
                if not to:
                    return
                await self._post(client, key, mail_from, to, event.subject, event.body)
        except httpx.HTTPError:
            logger.exception("Resend email notification failed")
