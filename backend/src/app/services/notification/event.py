from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class NotificationEvent:
    event_type: str
    subject: str
    body: str
    payload: dict[str, Any]
    user_ids: tuple[int, ...] = ()  # in-app: кому писать в хранилище; email/webhook игнорируют
