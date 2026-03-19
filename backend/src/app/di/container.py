from dishka import Container, Provider, provide, Scope

from security.jwt_provider import JWTProvider
from repositories.client_inmemory_repo import AsyncInMemoryClientRepository
from services.token_service import TokenService
from usecases.issue_token import IssueTokenUseCase


class AsyncAppProvider(Provider):
    scope = Scope.APP

    @provide
    async def jwt_provider(self) -> JWTProvider:
        # Синхронный провайдер остаётся sync, но можно менять на async, если понадобится
        return JWTProvider(public_key="PUBLIC_RSA_KEY")

    @provide
    async def client_repo(self) -> AsyncInMemoryClientRepository:
        repo = AsyncInMemoryClientRepository()
        # await repo.connect()  # подключение к БД
        return repo

    @provide
    async def token_service(self, jwt_provider: JWTProvider) -> TokenService:
        return TokenService(jwt_provider)

    @provide
    async def issue_token_uc(
        self,
        client_repo: AsyncInMemoryClientRepository,
        token_service: TokenService,
    ) -> IssueTokenUseCase:
        return IssueTokenUseCase(client_repo, token_service)


container = Container(AsyncAppProvider())