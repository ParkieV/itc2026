from datetime import datetime, timedelta, UTC
from entities.access_token import AccessToken

class IssueAccessTokenService:
    def __init__(self, jwt_provider):
        self.jwt_provider = jwt_provider

    def execute(self, subject: str, scope: str) -> AccessToken:
        expires = datetime.now(tz=UTC) + timedelta(hours=2)
        token = self.jwt_provider.encode(
            sub=subject,
            scope=scope,
            exp=expires,
        )
        return AccessToken(token, expires.isoformat(), scope)