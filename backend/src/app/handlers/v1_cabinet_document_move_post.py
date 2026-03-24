from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException

from services.change_doc_stage import exceptions
from usecases.change_doc_stage.usecase import ChangeDocumentStageUseCase
from .dtos.helper import openapi_responses
from .dtos.v1_change_doc_stage_post import (
    V1_CHANGE_DOC_STAGE_POST_RESPONSE200,
    V1_CHANGE_DOC_STAGE_POST_RESPONSE400,
    V1_CHANGE_DOC_STAGE_POST_RESPONSE404,
    V1ChangeDocStagePostRequest,
)

router = APIRouter()


@router.post(
    "/v1/cabinet/document/move",
    responses=openapi_responses(
        {
            200: V1_CHANGE_DOC_STAGE_POST_RESPONSE200,
            400: V1_CHANGE_DOC_STAGE_POST_RESPONSE400,
            404: V1_CHANGE_DOC_STAGE_POST_RESPONSE404,
        }
    ),
)
@inject
async def change_doc_stage(
    change_doc_stage_uc: FromDishka[ChangeDocumentStageUseCase],
    request: V1ChangeDocStagePostRequest,
) -> None:
    try:
        await change_doc_stage_uc.execute(request.doc_id, request.stage_id)
    except exceptions.StageNotFound as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found)) from err_not_found
    except exceptions.DocumentNotFound as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found)) from err_not_found
    except exceptions.InvalidTargetStage as err_invalid_target_stage:
        raise HTTPException(status_code=400, detail=str(err_invalid_target_stage)) from err_invalid_target_stage
    except exceptions.DocumentRevisionRequired as err_revision:
        raise HTTPException(status_code=400, detail=str(err_revision)) from err_revision
    except exceptions.ReviewsNotAllAccepted as err_reviews:
        raise HTTPException(status_code=400, detail=str(err_reviews)) from err_reviews
