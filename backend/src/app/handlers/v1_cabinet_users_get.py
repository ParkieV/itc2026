from dataclasses import asdict

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends

from handlers.dependencies.get_current_client_id import get_current_client_id
from services.get_users.service import GetUsersService
from .dtos.helper import openapi_responses
from .dtos.v1_cabinet_users_get import (
    V1CabinetUserGetResponse,
    V1_CABINET_USERS_GET_RESPONSE200,
    V1_CABINET_USERS_GET_RESPONSE401,
)

router = APIRouter()


@router.get(
    "/v1/cabinet/users",
    responses=openapi_responses(
        {
            200: V1_CABINET_USERS_GET_RESPONSE200,
            401: V1_CABINET_USERS_GET_RESPONSE401,
        }
    ),
)
@inject
async def cabinet_users(
    get_users_service: FromDishka[GetUsersService],
    _: str = Depends(get_current_client_id),
) -> list[V1CabinetUserGetResponse]:
    users = await get_users_service.execute()
    return [
        V1CabinetUserGetResponse.model_validate(asdict(user))
        for user in users
    ]

