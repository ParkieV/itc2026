from pydantic import BaseModel, Field


class V1CabinetClientGetResponse(BaseModel):
    fio: str
    login: str


class V1_CABINET_CLIENT_GET_RESPONSE200(V1CabinetClientGetResponse):
    """Данные профиля текущего клиента (из JWT)."""


class V1_CABINET_CLIENT_GET_RESPONSE401(BaseModel):
    """Невалидный, просроченный или отсутствующий токен."""

    detail: str = Field(description="Текст ошибки")


class V1_CABINET_CLIENT_GET_RESPONSE404(BaseModel):
    """Клиент не найден (id из JWT не существует в хранилище)."""

    detail: str = Field(description="Текст ошибки")
