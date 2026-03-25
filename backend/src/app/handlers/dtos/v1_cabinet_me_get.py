from pydantic import BaseModel, Field


class V1CabinetMeGetResponse(BaseModel):
    user_id: int
    fio: str
    login: str
    organization: str


class V1_CABINET_ME_GET_RESPONSE200(V1CabinetMeGetResponse):
    """Данные профиля текущего клиента (из JWT)."""


class V1_CABINET_ME_GET_RESPONSE401(BaseModel):
    """Невалидный, просроченный или отсутствующий токен."""

    detail: str = Field(description="Текст ошибки")


class V1_CABINET_ME_GET_RESPONSE404(BaseModel):
    """Клиент не найден (id из JWT не существует в хранилище)."""

    detail: str = Field(description="Текст ошибки")
