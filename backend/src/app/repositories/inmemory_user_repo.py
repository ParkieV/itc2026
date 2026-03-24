from typing import Final

import pandas as pd

from entities.user import User

class AsyncInMemoryUserRepository:
    _columns: Final = ["user_id", "login", "password", "scope", "fio", "email"]

    def __init__(self):
        self._users = pd.DataFrame(
            [
                {
                    "user_id": 1,
                    "login": "test_user",
                    "password": "password123",
                    "scope": "user",
                    "fio": "Тестовый Пользователь",
                    "email": "test_user@example.com",
                },
                {
                    "user_id": 2,
                    "login": "yarik",
                    "password": "password123",
                    "scope": "user",
                    "fio": "Тестовый Пользователь",
                    "email": "yarik@example.com",
                },
                {
                    "user_id": 3,
                    "login": "timosha",
                    "password": "password123",
                    "scope": "user",
                    "fio": "Тестовый Пользователь",
                    "email": "timosha@example.com",
                },
            ]
        ).set_index(["user_id", "login"])

    @property
    def users(self) -> pd.DataFrame:
        return self._users.copy()

    async def get_by_login(self, login: str) -> User | None:
        try:
            user_row = self.users.xs(login, level="login", drop_level=False)
        except KeyError:
            return None

        user_dict = user_row.reset_index().iloc[0].to_dict()
        return User(
            user_id=str(user_dict["user_id"]),
            login=user_dict["login"],
            password=user_dict["password"],
            scope=user_dict["scope"],
            fio=user_dict["fio"],
            email=str(user_dict.get("email", "") or ""),
        )

    async def get_by_id(self, user_id: int) -> User | None:
        try:
            user_row = self.users.xs(user_id, level="user_id", drop_level=False)
        except KeyError:
            return None

        user_dict = user_row.reset_index().iloc[0].to_dict()
        return User(
            user_id=str(user_dict["user_id"]),
            login=user_dict["login"],
            password=user_dict["password"],
            scope=user_dict["scope"],
            fio=user_dict["fio"],
            email=str(user_dict.get("email", "") or ""),
        )