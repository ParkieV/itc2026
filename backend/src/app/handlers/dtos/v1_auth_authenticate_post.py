from pydantic import BaseModel, Field


class V1AuthAuthenticatePostResponse(BaseModel):
    access_token: str
    token_type: str


class V1_AUTH_AUTHENTICATE_POST_RESPONSE200(V1AuthAuthenticatePostResponse):
    """Успешная аутентификация; в теле access_token и token_type (Bearer)."""


class V1_AUTH_AUTHENTICATE_POST_RESPONSE400(BaseModel):
    """Неверный пароль."""

    detail: str = Field(description="Текст ошибки")


class V1_AUTH_AUTHENTICATE_POST_RESPONSE404(BaseModel):
    """Пользователь с указанным логином не найден."""

    detail: str = Field(description="Текст ошибки")
