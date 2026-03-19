from repositories.client_inmemory_repo import AsyncInMemoryClientRepository
from services.token_service import TokenService
from vo.scope import Scope

class IssueTokenUseCase:
    def __init__(self, client_repo: AsyncInMemoryClientRepository, token_service: TokenService):
        self.client_repo = client_repo
        self.token_service = token_service

    async def execute(self, client_id: str, client_secret: str, scope: str):
        client = await self.client_repo.get(client_id)
        if not client or client.client_secret != client_secret:
            raise ValueError("invalid_client")

        scope_vo = Scope(scope)
        if not scope_vo.is_allowed(client.scopes):
            raise ValueError("invalid_scope")

        return self.token_service.issue_access_token(client_id, scope)