import os
from pathlib import Path

from dishka import Provider, provide, Scope, make_async_container

from config import AppConfig, JWTSettings, HTTPServerSettings
from security.jwt_provider import JWTProvider
from repositories.inmemory_document_repo import InMemoryDocumentRepository
from services.get_origin_document.service import GetOriginDocumentService
from services.get_pdf_document.service import GetPdfDocumentService
from repositories.inmemory_stage_reviewers_repo import AsyncInMemoryStageReviewersRepository
from repositories.inmemory_stages_repo import AsyncInMemoryStagesRepository
from repositories.inmemory_user_repo import AsyncInMemoryUserRepository
from services.authenticate_user.service import AuthenticateUserService
from services.get_stages_service.service import GetStagesService
from services.get_user.service import GetUserService
from services.issue_access_token import IssueAccessTokenService
from usecases.authorize_user.usecase import AuthorizeUserUseCase
from usecases.get_stages_with_reviewer_and_docs.usecase import GetStagesWithReviewerAndDocsUseCase

_ENV_PATH = os.environ.get("ENV_PATH", None)

class AsyncAppProvider(Provider):
    scope = Scope.APP

    @provide
    async def jwt_provider(self, jwt_settings: JWTSettings) -> JWTProvider:
        return JWTProvider(
            jwt_settings.private_key_path,
            jwt_settings.public_key_path,
            jwt_settings.algorithm,
        )

    @provide
    async def user_repo(self) -> AsyncInMemoryUserRepository:
        repo = AsyncInMemoryUserRepository()
        # await repo.connect()  # подключение к БД
        return repo

    @provide
    async def document_repo(self) -> InMemoryDocumentRepository:
        return InMemoryDocumentRepository()

    @provide
    async def stages_repo(self) -> AsyncInMemoryStagesRepository:
        return AsyncInMemoryStagesRepository()

    @provide
    async def stage_reviewers_repo(self) -> AsyncInMemoryStageReviewersRepository:
        return AsyncInMemoryStageReviewersRepository()

    @provide
    async def authenticate_user_service(self, user_repo: AsyncInMemoryUserRepository) -> AuthenticateUserService:
        return AuthenticateUserService(user_repo)

    @provide
    async def token_service(self, jwt_provider: JWTProvider) -> IssueAccessTokenService:
        return IssueAccessTokenService(jwt_provider)

    @provide
    async def authorize_user_uc(
        self,
        authenticate_user_service: AuthenticateUserService,
        issue_access_token_service: IssueAccessTokenService,
    ) -> AuthorizeUserUseCase:
        return AuthorizeUserUseCase(authenticate_user_service, issue_access_token_service)

    @provide
    async def get_user_service(
        self,
        user_repo: AsyncInMemoryUserRepository,
    ) -> GetUserService:
        return GetUserService(user_repo)

    @provide
    async def get_pdf_document_service(
        self,
        document_repo: InMemoryDocumentRepository,
    ) -> GetPdfDocumentService:
        return GetPdfDocumentService(document_repo)

    @provide
    async def get_origin_document_service(
            self,
            document_repo: InMemoryDocumentRepository,
    ) -> GetOriginDocumentService:
        return GetOriginDocumentService(document_repo)

    @provide
    async def get_stages_service(
        self,
        stages_repo: AsyncInMemoryStagesRepository,
    ) -> GetStagesService:
        return GetStagesService(stages_repo)

    @provide
    async def get_stages_with_reviewer_and_docs_uc(
        self,
        stages_repo: AsyncInMemoryStagesRepository,
        stage_reviewers_repo: AsyncInMemoryStageReviewersRepository,
        user_repo: AsyncInMemoryUserRepository,
    ) -> GetStagesWithReviewerAndDocsUseCase:
        return GetStagesWithReviewerAndDocsUseCase(
            stages_repo,
            stage_reviewers_repo,
            user_repo,
        )


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    async def app_config(self) -> AppConfig:
        return AppConfig(_env_file=_ENV_PATH)

    @provide(scope=Scope.APP)
    async def jwt_settings(self) -> JWTSettings:
        return JWTSettings(_env_file=_ENV_PATH)

    @provide(scope=Scope.APP)
    async def http_server_settings(self) -> HTTPServerSettings:
        return HTTPServerSettings(_env_file=_ENV_PATH)


container = make_async_container(ConfigProvider(), AsyncAppProvider())
