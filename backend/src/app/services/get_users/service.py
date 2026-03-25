from entities.user import User
from repositories.inmemory_user_repo import AsyncInMemoryUserRepository


class GetUsersService:
    def __init__(self, user_repo: AsyncInMemoryUserRepository):
        self._user_repo = user_repo

    async def execute(self) -> list[User]:
        # In-memory repo uses pandas; we build entities from all rows.
        users_df = self._user_repo.users.reset_index().sort_values(by="user_id")
        records = users_df.to_dict(orient="records")

        out: list[User] = []
        for user_dict in records:
            out.append(
                User(
                    user_id=str(user_dict["user_id"]),
                    login=user_dict["login"],
                    password=user_dict["password"],
                    scope=user_dict["scope"],
                    fio=user_dict["fio"],
                    email=str(user_dict.get("email", "") or ""),
                    organization=user_dict["organization"],
                    phone=user_dict["phone"],
                )
            )

        return out

