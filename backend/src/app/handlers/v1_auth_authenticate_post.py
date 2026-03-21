from dishka.integrations.fastapi import inject, FromDishka
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from usecases.authorize_user.usecase import AuthorizeUserUseCase
from usecases.authorize_user import exceptions
from .dtos.v1_auth_authenticate_post import V1AuthAuthenticatePostResponse

router = APIRouter()

@router.post('/v1/auth/authenticate')
@inject
async def authenticate(
        authorize_user_uc: FromDishka[AuthorizeUserUseCase],
        form_data: OAuth2PasswordRequestForm = Depends(),
) -> V1AuthAuthenticatePostResponse:
    try:
        access_token = await authorize_user_uc.execute(form_data.username, form_data.password)
    except exceptions.UserNotFound as err_user_not_found:
        raise HTTPException(status_code=404, detail=str(err_user_not_found))
    except exceptions.InvalidPassword as err_invalid_password:
        raise HTTPException(status_code=400, detail=str(err_invalid_password))

    return V1AuthAuthenticatePostResponse(
        access_token=access_token.value,
        token_type="Bearer"
    )