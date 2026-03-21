from entities.user import User
from repositories.inmemory_user_repo import AsyncInMemoryUserRepository
from .exceptions import UserNotFound, InvalidPassword


class AuthenticateUserService:
    def __init__(self, user_repo: AsyncInMemoryUserRepository):
        self._user_repo = user_repo

    async def execute(self, login: str, password: str) -> User:
        user = await self._user_repo.get_by_login(login)
        if user is None:
            raise UserNotFound(f"user with login={login} not found")
        if user.password != password:
            raise InvalidPassword(f"user with login={login} has invalid password")

        return user