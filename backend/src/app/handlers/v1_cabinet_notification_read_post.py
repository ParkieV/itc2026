from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException, status

from handlers.dependencies.get_current_client_id import get_current_client_id
from services.user_in_app_notification.exceptions import UserNotificationNotFound
from services.user_in_app_notification.service import UserInAppNotificationService
from .dtos.helper import openapi_responses
from .dtos.v1_cabinet_notification_read_post import (
    V1_CABINET_NOTIFICATION_READ_POST_RESPONSE204,
    V1_CABINET_NOTIFICATION_READ_POST_RESPONSE401,
    V1_CABINET_NOTIFICATION_READ_POST_RESPONSE404,
)

router = APIRouter()


@router.post(
    "/v1/cabinet/notifications/{notification_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=openapi_responses(
        {
            204: V1_CABINET_NOTIFICATION_READ_POST_RESPONSE204,
            401: V1_CABINET_NOTIFICATION_READ_POST_RESPONSE401,
            404: V1_CABINET_NOTIFICATION_READ_POST_RESPONSE404,
        }
    ),
)
@inject
async def mark_notification_read(
    notification_service: FromDishka[UserInAppNotificationService],
    notification_id: int,
    client_id: str = Depends(get_current_client_id),
) -> None:
    try:
        await notification_service.mark_read(notification_id, int(client_id))
    except UserNotificationNotFound as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err)) from err
