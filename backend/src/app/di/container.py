import os
from pathlib import Path

from dishka import Provider, provide, Scope, make_async_container

from config import AppConfig, JWTSettings, HTTPServerSettings
from repositories.inmemory_comments_repo import AsyncInMemoryCommentsRepository
from security.jwt_provider import JWTProvider
from repositories.inmemory_document_repo import InMemoryDocumentRepository
from repositories.inmemory_reviews_repo import AsyncInMemoryReviewsRepository
from services.get_origin_document.service import GetOriginDocumentService
from services.create_comment.service import CreateCommentService
from services.patch_comment.service import PatchCommentService
from services.get_comments_by_doc.service import GetCommentsByDocService
from services.get_comments_by_doc_and_stage.service import GetCommentsByDocAndStageService
from services.get_pdf_document.service import GetPdfDocumentService
from repositories.inmemory_stages_repo import AsyncInMemoryStagesRepository
from repositories.inmemory_user_repo import AsyncInMemoryUserRepository
from services.authenticate_user.service import AuthenticateUserService
from services.change_review_aprove_status.service import ChangeReviewAproveStatusService
from services.change_review_view_status.service import ChangeReviewViewStatusService
from services.get_stage_by_id.service import GetStageByIdService
from services.get_stages_service.service import GetStagesService
from services.get_user.service import GetUserService
from services.issue_access_token import IssueAccessTokenService
from services.setup_reviewer.service import SetupReviewerService
from usecases.authorize_user.usecase import AuthorizeUserUseCase
from usecases.get_document_detail.usecase import GetDocumentDetailUseCase
from usecases.get_stages_with_reviewer_and_docs.usecase import GetStagesWithReviewerAndDocsUseCase


_ENV_PATH = os.environ.get("ENV_PATH")

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
    async def reviews_repo(self) -> AsyncInMemoryReviewsRepository:
        return AsyncInMemoryReviewsRepository()

    @provide
    async def comments_repo(self) -> AsyncInMemoryCommentsRepository:
        return AsyncInMemoryCommentsRepository()

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
    async def get_stage_by_id_service(
        self,
        stages_repo: AsyncInMemoryStagesRepository,
    ) -> GetStageByIdService:
        return GetStageByIdService(stages_repo)

    @provide
    async def change_review_view_status_service(
        self,
        reviews_repo: AsyncInMemoryReviewsRepository,
        get_user_service: GetUserService,
        get_stage_by_id_service: GetStageByIdService,
        get_pdf_document_service: GetPdfDocumentService,
    ) -> ChangeReviewViewStatusService:
        return ChangeReviewViewStatusService(
            reviews_repo,
            get_user_service,
            get_stage_by_id_service,
            get_pdf_document_service,
        )

    @provide
    async def change_review_aprove_status_service(
        self,
        reviews_repo: AsyncInMemoryReviewsRepository,
        get_user_service: GetUserService,
        get_stage_by_id_service: GetStageByIdService,
        get_pdf_document_service: GetPdfDocumentService,
    ) -> ChangeReviewAproveStatusService:
        return ChangeReviewAproveStatusService(
            reviews_repo,
            get_user_service,
            get_stage_by_id_service,
            get_pdf_document_service,
        )

    @provide
    async def setup_reviewer_service(
        self,
        reviews_repo: AsyncInMemoryReviewsRepository,
        get_user_service: GetUserService,
        get_stage_by_id_service: GetStageByIdService,
        get_pdf_document_service: GetPdfDocumentService,
    ) -> SetupReviewerService:
        return SetupReviewerService(
            reviews_repo,
            get_user_service,
            get_stage_by_id_service,
            get_pdf_document_service,
        )

    @provide
    async def get_comments_by_doc_and_stage_service(
        self,
        comments_repo: AsyncInMemoryCommentsRepository,
        get_pdf_document_service: GetPdfDocumentService,
        get_stage_by_id_service: GetStageByIdService,
    ) -> GetCommentsByDocAndStageService:
        return GetCommentsByDocAndStageService(
            comments_repo,
            get_pdf_document_service,
            get_stage_by_id_service,
        )

    @provide
    async def get_comments_by_doc_service(
        self,
        comments_repo: AsyncInMemoryCommentsRepository,
        get_pdf_document_service: GetPdfDocumentService,
        get_stage_by_id_service: GetStageByIdService,
    ) -> GetCommentsByDocService:
        return GetCommentsByDocService(
            comments_repo,
            get_pdf_document_service,
            get_stage_by_id_service,
        )

    @provide
    async def create_comment_service(
        self,
        comments_repo: AsyncInMemoryCommentsRepository,
        get_pdf_document_service: GetPdfDocumentService,
        get_stage_by_id_service: GetStageByIdService,
        get_user_service: GetUserService,
    ) -> CreateCommentService:
        return CreateCommentService(
            comments_repo,
            get_pdf_document_service,
            get_stage_by_id_service,
            get_user_service,
        )

    @provide
    async def patch_comment_service(
        self,
        comments_repo: AsyncInMemoryCommentsRepository,
        get_pdf_document_service: GetPdfDocumentService,
    ) -> PatchCommentService:
        return PatchCommentService(comments_repo, get_pdf_document_service)

    @provide
    async def get_document_detail_uc(
        self,
        get_pdf_document_service: GetPdfDocumentService,
        reviews_repo: AsyncInMemoryReviewsRepository,
        comments_repo: AsyncInMemoryCommentsRepository,
    ) -> GetDocumentDetailUseCase:
        return GetDocumentDetailUseCase(
            get_pdf_document_service,
            reviews_repo,
            comments_repo,
        )

    @provide
    async def get_stages_with_reviewer_and_docs_uc(
        self,
        stages_repo: AsyncInMemoryStagesRepository,
        reviews_repo: AsyncInMemoryReviewsRepository,
        user_repo: AsyncInMemoryUserRepository,
        document_repo: InMemoryDocumentRepository,
    ) -> GetStagesWithReviewerAndDocsUseCase:
        return GetStagesWithReviewerAndDocsUseCase(
            stages_repo,
            document_repo,
            reviews_repo,
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
