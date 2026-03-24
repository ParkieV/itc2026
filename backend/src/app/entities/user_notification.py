from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class UserNotification:
    id: int
    user_id: int
    event_type: str
    title: str
    body: str
    payload: dict[str, Any]
    read: bool
    created_at: int
