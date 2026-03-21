from entities.user import User
from repositories.inmemory_user_repo import AsyncInMemoryUserRepository
from .exceptions import UserNotFound


class GetUserService:
    def __init__(self, user_repo: AsyncInMemoryUserRepository):
        self._user_repo = user_repo

    async def execute(self, user_id: int) -> User:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFound(f"user with id={user_id} not found")

        return user