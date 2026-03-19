from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True, slots=True)
class AccessToken:
    value: str
    expires_at: datetime
    scope: str