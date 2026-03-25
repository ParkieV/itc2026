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
                    "login": "stepa",
                    "password": "password123",
                    "scope": "user",
                    "fio": "Степан Пискунов",
                    "email": "quarioo@mail.ru",
                    "organization": "Организация ООО Телеком",
                    "phone": "+79991234567",
                },
                {
                    "user_id": 2,
                    "login": "yarik",
                    "password": "password123",
                    "scope": "user",
                    "fio": "Ярослав Сокин",
                    "email": "kinsoprod@yandex.ru",
                    "organization": "Юридическая комисия",
                    "phone": "+79991234568",
                },
                {
                    "user_id": 3,
                    "login": "nikita",
                    "password": "password123",
                    "scope": "user",
                    "fio": "Никита Крылов",
                    "email": "m2206041@edu.misis.ru",
                    "organization": "Правительство Тульской области",
                    "phone": "+79991234569",
                },
                {
                    "user_id": 4,
                    "login": "timosha",
                    "password": "password123",
                    "scope": "user",
                    "fio": "Костров Тимофей",
                    "email": "m2206041@edu.misis.ru",
                    "organization": "Исполняющая организация",
                    "phone": "+79991234569",
                }
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
            organization=user_dict["organization"],
            phone=user_dict["phone"],
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
            organization=user_dict["organization"],
            phone=user_dict["phone"],
        )