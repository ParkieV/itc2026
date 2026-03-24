from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from entities.user_notification import UserNotification


class InMemoryUserNotificationsRepository:
    @staticmethod
    def _now_msk_timestamp() -> int:
        return int(datetime.now(ZoneInfo("Europe/Moscow")).timestamp())

    def __init__(self) -> None:
        self._items: dict[int, dict[str, Any]] = {}
        self._next_id = 1

    async def add(
        self,
        user_id: int,
        event_type: str,
        title: str,
        body: str,
        payload: dict[str, Any],
        *,
        read: bool = False,
    ) -> int:
        nid = self._next_id
        self._next_id += 1
        self._items[nid] = {
            "id": nid,
            "user_id": user_id,
            "event_type": event_type,
            "title": title,
            "body": body,
            "payload": dict(payload),
            "read": read,
            "created_at": self._now_msk_timestamp(),
        }
        return nid

    async def list_unread_for_user(self, user_id: int) -> list[UserNotification]:
        out: list[UserNotification] = []
        for row in self._items.values():
            if row["user_id"] != user_id or row["read"]:
                continue
            out.append(self._to_entity(row))
        out.sort(key=lambda n: n.created_at, reverse=True)
        return out

    async def mark_read(self, notification_id: int, user_id: int) -> bool:
        row = self._items.get(notification_id)
        if row is None or row["user_id"] != user_id:
            return False
        row["read"] = True
        return True

    def _to_entity(self, row: dict[str, Any]) -> UserNotification:
        return UserNotification(
            id=row["id"],
            user_id=row["user_id"],
            event_type=row["event_type"],
            title=row["title"],
            body=row["body"],
            payload=row["payload"],
            read=row["read"],
            created_at=row["created_at"],
        )
