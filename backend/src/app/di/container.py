import os
from pathlib import Path

from dishka import Provider, provide, Scope, make_async_container

from config import AppConfig, JWTSettings, HTTPServerSettings
from repositories.inmemory_document_files_repo import InMemoryDocumentFilesRepository
from security.jwt_provider import JWTProvider
from repositories.inmemory_document_repo import InMemoryDocumentRepository
from repositories.inmemory_user_repo import AsyncInMemoryUserRepository
from services.add_document.service import AddDocumentService
from services.add_origin_document_file.service import AddOriginDocumentFileService
from services.authenticate_user.service import AuthenticateUserService
from services.save_pdf_document_file.service import SavePdfDocumentFileService
from services.get_user.service import GetUserService
from services.issue_access_token import IssueAccessTokenService
from usecases.authorize_user.usecase import AuthorizeUserUseCase
from usecases.create_document_file.usecase import CreateDocumentFileUseCase
from services.get_origin_document.service import GetOriginDocumentService
from services.get_pdf_document.service import GetPdfDocumentService
from repositories.inmemory_stage_reviewers_repo import AsyncInMemoryStageReviewersRepository
from repositories.inmemory_stages_repo import AsyncInMemoryStagesRepository
from services.change_doc_stage.service import ChangeDocumentStageService
from services.get_stage_by_id.service import GetStageByIdService
from services.get_stages_service.service import GetStagesService
from usecases.change_doc_stage.usecase import ChangeDocumentStageUseCase
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
    async def document_files_repo(self) -> InMemoryDocumentFilesRepository:
        return InMemoryDocumentFilesRepository()

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
        document_files_repo: InMemoryDocumentFilesRepository,
    ) -> GetPdfDocumentService:
        return GetPdfDocumentService(document_repo, document_files_repo)

    @provide
    async def get_origin_document_service(
            self,
            document_repo: InMemoryDocumentRepository,
            document_files_repo: InMemoryDocumentFilesRepository,
    ) -> GetOriginDocumentService:
        return GetOriginDocumentService(document_repo, document_files_repo)

    @provide
    async def add_origin_document_file_service(
        self,
        document_files_repo: InMemoryDocumentFilesRepository,
    ) -> AddOriginDocumentFileService:
        return AddOriginDocumentFileService(document_files_repo)

    @provide
    async def save_pdf_document_file_service(
        self,
        document_files_repo: InMemoryDocumentFilesRepository,
    ) -> SavePdfDocumentFileService:
        return SavePdfDocumentFileService(document_files_repo)

    @provide
    async def add_document_service(
        self,
        document_repo: InMemoryDocumentRepository,
    ) -> AddDocumentService:
        return AddDocumentService(document_repo)

    @provide
    async def create_document_file_use_case(
        self,
        get_user_service: GetUserService,
        add_document_service: AddDocumentService,
        add_origin_document_file_service: AddOriginDocumentFileService,
        save_pdf_document_file_service: SavePdfDocumentFileService,
    ) -> CreateDocumentFileUseCase:
        return CreateDocumentFileUseCase(
            get_user_service=get_user_service,
            add_document_service=add_document_service,
            add_origin_document_file_service=add_origin_document_file_service,
            save_pdf_document_file_service=save_pdf_document_file_service,
        )

    @provide
    async def change_document_stage_service(
        self,
        document_repo: InMemoryDocumentRepository,
    ) -> ChangeDocumentStageService:
        return ChangeDocumentStageService(document_repo)

    @provide
    async def get_stages_service(
        self,
        stages_repo: AsyncInMemoryStagesRepository,
    ) -> GetStagesService:
        return GetStagesService(stages_repo)

    @provide
    async def get_stage_by_id_service(
        self,
        stages_repo: AsyncInMemoryStagesRepository,
    ) -> GetStageByIdService:
        return GetStageByIdService(stages_repo)

    @provide
    async def get_stages_with_reviewer_and_docs_uc(
        self,
        stages_repo: AsyncInMemoryStagesRepository,
        document_repo: InMemoryDocumentRepository,
        stage_reviewers_repo: AsyncInMemoryStageReviewersRepository,
        user_repo: AsyncInMemoryUserRepository,
    ) -> GetStagesWithReviewerAndDocsUseCase:
        return GetStagesWithReviewerAndDocsUseCase(
            stages_repo,
            document_repo,
            stage_reviewers_repo,
            user_repo,
        )

    @provide
    async def change_doc_stage_uc(
        self,
        get_pdf_document_service: GetPdfDocumentService,
        change_document_stage_service: ChangeDocumentStageService,
        get_stage_by_id_service: GetStageByIdService,
    ) -> ChangeDocumentStageUseCase:
        return ChangeDocumentStageUseCase(
            get_pdf_document_service,
            change_document_stage_service,
            get_stage_by_id_service,
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
