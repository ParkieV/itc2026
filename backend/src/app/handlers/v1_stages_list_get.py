from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends
from entities.stage_with_reviewer_and_docs import StageWithReviewerAndDocs
from handlers.dependencies.get_current_client_id import get_current_client_id
from usecases.get_stages_with_reviewer_and_docs.usecase import GetStagesWithReviewerAndDocsUseCase

from .dtos.helper import openapi_responses
from .dtos.v1_stages_list_get import (
    StageReviewerUserGetResponse,
    StageSummaryGetResponse,
    V1_STAGES_LIST_GET_RESPONSE200,
    V1_STAGES_LIST_GET_RESPONSE401,
    V1StageWithReviewerAndDocsGetResponse,
)

router = APIRouter()


@router.get(
    "/v1/stages",
    responses=openapi_responses(
        {
            200: V1_STAGES_LIST_GET_RESPONSE200,
            401: V1_STAGES_LIST_GET_RESPONSE401,
        }
    ),
)
@inject
async def list_stages(
    get_stages_with_reviewer_and_docs_uc: FromDishka[GetStagesWithReviewerAndDocsUseCase],
    _: str = Depends(get_current_client_id),
) -> list[V1StageWithReviewerAndDocsGetResponse]:
    stages = await get_stages_with_reviewer_and_docs_uc.execute()
    return [_stage_with_reviewer_and_docs_to_response(i) for i in stages]


def _stage_with_reviewer_and_docs_to_response(
    row: StageWithReviewerAndDocs,
) -> V1StageWithReviewerAndDocsGetResponse:
    return V1StageWithReviewerAndDocsGetResponse(
        stage=StageSummaryGetResponse(
            stage_id=row.stage.stage_id,
            next_stage=row.stage.next_stage,
            title=row.stage.title,
        ),
        docs=list(row.docs),
        reviewers=[
            StageReviewerUserGetResponse(
                user_id=u.user_id,
                fio=u.fio,
            )
            for u in row.reviewers
        ],
    )

