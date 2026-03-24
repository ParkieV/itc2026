from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends

from handlers.dependencies.get_current_client_id import get_current_client_id
from services.user_in_app_notification.service import UserInAppNotificationService
from .dtos.helper import openapi_responses
from .dtos.v1_cabinet_notifications_unread_get import (
    V1_CABINET_NOTIFICATIONS_UNREAD_GET_RESPONSE200,
    V1_CABINET_NOTIFICATIONS_UNREAD_GET_RESPONSE401,
    V1CabinetNotificationUnreadItem,
    V1CabinetNotificationsUnreadGetResponse,
)

router = APIRouter()


@router.get(
    "/v1/cabinet/notifications/unread",
    responses=openapi_responses(
        {
            200: V1_CABINET_NOTIFICATIONS_UNREAD_GET_RESPONSE200,
            401: V1_CABINET_NOTIFICATIONS_UNREAD_GET_RESPONSE401,
        }
    ),
)
@inject
async def list_unread_notifications(
    notification_service: FromDishka[UserInAppNotificationService],
    client_id: str = Depends(get_current_client_id),
) -> V1CabinetNotificationsUnreadGetResponse:
    items = await notification_service.list_unread(int(client_id))
    return V1CabinetNotificationsUnreadGetResponse(
        items=[
            V1CabinetNotificationUnreadItem(
                id=n.id,
                event_type=n.event_type,
                title=n.title,
                body=n.body,
                payload=n.payload,
                created_at=n.created_at,
            )
            for n in items
        ]
    )
