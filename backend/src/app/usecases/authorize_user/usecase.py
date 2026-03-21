import entities
from services.authenticate_user.service import AuthenticateUserService
from services.issue_access_token import IssueAccessTokenService


class AuthorizeUserUseCase:
    def __init__(
        self,
        authenticate_user_service: AuthenticateUserService,
        issue_access_token_service: IssueAccessTokenService,
    ):
        self._authenticate_user_service = authenticate_user_service
        self._issue_access_token_service = issue_access_token_service

    async def execute(self, login: str, password: str) -> entities.AccessToken:
        user = await self._authenticate_user_service.execute(login, password)

        access_token = self._issue_access_token_service.execute(user.user_id, user.scope)

        return access_token
