from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Client:
    client_id: str
    client_secret: str
    scopes: set[str]
    redirect_uris: set[str]