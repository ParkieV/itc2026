from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException

from handlers.dependencies.get_current_client_id import get_current_client_id
from services.change_review_aprove_status.service import ChangeReviewAproveStatusService
from services.change_review_view_status.service import ChangeReviewViewStatusService
from services.get_pdf_document.exceptions import DocumentNotFound
from services.get_stage_by_id.exceptions import StageNotFound
from services.get_user.exceptions import UserNotFound
from services.setup_reviewer.exceptions import ReviewAlreadyExists
from services.setup_reviewer.service import SetupReviewerService
from .dtos.helper import openapi_responses
from .dtos.v1_cabinet_reviews_post import (
    V1_CABINET_REVIEWS_POST_RESPONSE400,
    V1_CABINET_REVIEWS_POST_RESPONSE200,
    V1_CABINET_REVIEWS_APROVE_POST_RESPONSE200,
    V1_CABINET_REVIEWS_POST_RESPONSE401,
    V1_CABINET_REVIEWS_POST_RESPONSE404,
    V1_CABINET_REVIEWS_VIEW_POST_RESPONSE200,
    V1CabinetReviewsCreateRequest,
    V1CabinetReviewsUpdateRequest,
)

router = APIRouter()


@router.post(
    "/v1/cabinet/reviews",
    responses=openapi_responses(
        {
            200: V1_CABINET_REVIEWS_POST_RESPONSE200,
            400: V1_CABINET_REVIEWS_POST_RESPONSE400,
            401: V1_CABINET_REVIEWS_POST_RESPONSE401,
            404: V1_CABINET_REVIEWS_POST_RESPONSE404,
        }
    ),
)
@inject
async def cabinet_reviews_create(
    request: V1CabinetReviewsCreateRequest,
    setup_reviewer_service: FromDishka[SetupReviewerService],
) -> None:
    try:
        await setup_reviewer_service.execute(
            doc_id=request.doc_id,
            user_id=request.user_id,
            stage_id=request.stage_id,
        )
    except ReviewAlreadyExists as err_already_exists:
        raise HTTPException(status_code=400, detail=str(err_already_exists)) from err_already_exists
    except (UserNotFound, StageNotFound, DocumentNotFound) as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found)) from err_not_found


@router.post(
    "/v1/cabinet/reviews/view",
    responses=openapi_responses(
        {
            200: V1_CABINET_REVIEWS_VIEW_POST_RESPONSE200,
            401: V1_CABINET_REVIEWS_POST_RESPONSE401,
            404: V1_CABINET_REVIEWS_POST_RESPONSE404,
        }
    ),
)
@inject
async def cabinet_reviews_view(
    request: V1CabinetReviewsUpdateRequest,
    change_review_view_status_service: FromDishka[ChangeReviewViewStatusService],
    user_id: str = Depends(get_current_client_id),
) -> None:
    try:
        await change_review_view_status_service.execute(
            doc_id=request.doc_id,
            user_id=int(user_id),
            stage_id=request.stage_id,
            is_viewed=True,
        )
    except (UserNotFound, StageNotFound, DocumentNotFound) as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found)) from err_not_found


@router.post(
    "/v1/cabinet/reviews/aprove",
    responses=openapi_responses(
        {
            200: V1_CABINET_REVIEWS_APROVE_POST_RESPONSE200,
            401: V1_CABINET_REVIEWS_POST_RESPONSE401,
            404: V1_CABINET_REVIEWS_POST_RESPONSE404,
        }
    ),
)
@inject
async def cabinet_reviews_aprove(
    request: V1CabinetReviewsUpdateRequest,
    change_review_aprove_status_service: FromDishka[ChangeReviewAproveStatusService],
    user_id: str = Depends(get_current_client_id),
) -> None:
    try:
        await change_review_aprove_status_service.execute(
            doc_id=request.doc_id,
            user_id=int(user_id),
            stage_id=request.stage_id,
            is_aproved=True,
        )
    except (UserNotFound, StageNotFound, DocumentNotFound) as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found)) from err_not_found
