from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException, status

from handlers.dependencies.verify_internal_notification_key import verify_internal_notification_key
from services.get_user.exceptions import UserNotFound
from usecases.create_in_app_user_notification.usecase import CreateInAppUserNotificationUseCase
from .dtos.helper import openapi_responses
from .dtos.v1_user_notifications_post import (
    V1_USER_NOTIFICATIONS_POST_RESPONSE200,
    V1_USER_NOTIFICATIONS_POST_RESPONSE403,
    V1_USER_NOTIFICATIONS_POST_RESPONSE404,
    V1UserNotificationsPostRequest,
    V1UserNotificationsPostResponse,
)

router = APIRouter()


@router.post(
    "/v1/user-notifications",
    responses=openapi_responses(
        {
            200: V1_USER_NOTIFICATIONS_POST_RESPONSE200,
            403: V1_USER_NOTIFICATIONS_POST_RESPONSE403,
            404: V1_USER_NOTIFICATIONS_POST_RESPONSE404,
        }
    ),
)
@inject
async def create_user_notification(
    uc: FromDishka[CreateInAppUserNotificationUseCase],
    body: V1UserNotificationsPostRequest,
    _auth: None = Depends(verify_internal_notification_key),
) -> V1UserNotificationsPostResponse:
    try:
        nid = await uc.execute(
            user_id=body.user_id,
            event_type=body.event_type,
            title=body.title,
            body=body.body,
            payload=body.payload,
        )
    except UserNotFound as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err)) from err
    return V1UserNotificationsPostResponse(notification_id=nid)
