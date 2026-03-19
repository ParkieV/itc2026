from datetime import datetime, timedelta, UTC
from .entities.access_token import AccessToken

class TokenService:
    def __init__(self, jwt_provider):
        self.jwt_provider = jwt_provider

    def issue_access_token(self, subject: str, scope: str) -> AccessToken:
        expires = datetime.now(tz=UTC) + timedelta(minutes=15)
        token = self.jwt_provider.encode(
            sub=subject,
            scope=scope,
            exp=expires,
        )
        return AccessToken(token, expires, scope)