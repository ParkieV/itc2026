from dataclasses import asdict

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends, HTTPException, APIRouter

from handlers.dependencies.get_current_client_id import get_current_client_id
from services.get_user.service import GetUserService
from services.get_user import exceptions
from .dtos.helper import openapi_responses
from .dtos.v1_cabinet_me_get import (
    V1_CABINET_ME_GET_RESPONSE200,
    V1_CABINET_ME_GET_RESPONSE401,
    V1_CABINET_ME_GET_RESPONSE404,
    V1CabinetMeGetResponse,
)

router = APIRouter()


@router.get(
    "/v1/cabinet/me",
    responses=openapi_responses(
        {
            200: V1_CABINET_ME_GET_RESPONSE200,
            401: V1_CABINET_ME_GET_RESPONSE401,
            404: V1_CABINET_ME_GET_RESPONSE404,
        }
    ),
)
@inject
async def cabinet_client(
        get_user_service: FromDishka[GetUserService],
        client_id: str = Depends(get_current_client_id)
) -> V1CabinetMeGetResponse:
    try:
        user = await get_user_service.execute(int(client_id))
    except exceptions.UserNotFound as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found))

    return V1CabinetMeGetResponse.model_validate(
        asdict(user)
    )