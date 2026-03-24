from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AccessToken:
    value: str
    expires_at: str
    scope: str