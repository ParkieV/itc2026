from pydantic import BaseModel, Field, RootModel


class V1CabinetUserGetResponse(BaseModel):
    user_id: int
    fio: str
    login: str
    organization: str
    phone: str = Field(default="", description="Телефон пользователя")
    email: str = Field(default="", description="Email пользователя")


class V1_CABINET_USERS_GET_RESPONSE200(RootModel[list[V1CabinetUserGetResponse]]):
    """Список всех пользователей."""


class V1_CABINET_USERS_GET_RESPONSE401(BaseModel):
    """Невалидный, просроченный или отсутствующий токен."""

    detail: str = Field(description="Текст ошибки")

