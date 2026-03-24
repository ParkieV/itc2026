"""Единый формат моментов времени в приложении: ISO 8601 (строка с часовым поясом)."""

from datetime import datetime
from zoneinfo import ZoneInfo

MSK = ZoneInfo("Europe/Moscow")


def now_iso_msk() -> str:
    return datetime.now(MSK).isoformat()


def from_unix_seconds_iso_msk(seconds: int) -> str:
    return datetime.fromtimestamp(seconds, tz=MSK).isoformat()
