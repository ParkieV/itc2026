from dataclasses import asdict

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends, HTTPException, APIRouter

from handlers.dependencies.get_current_client_id import get_current_client_id
from services.get_user.service import GetUserService
from services.get_user import exceptions
from .dtos.v1_cabinet_client_get import V1CabinetClientGetResponse

router = APIRouter()

@router.get("/v1/cabinet/client")
@inject
async def cabinet_client(
        get_client_service: FromDishka[GetUserService],
        client_id: str = Depends(get_current_client_id)
) -> V1CabinetClientGetResponse:
    try:
        client = await get_client_service.execute(int(client_id))
    except exceptions.UserNotFound as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found))

    return V1CabinetClientGetResponse.model_validate(
        asdict(client)
    )