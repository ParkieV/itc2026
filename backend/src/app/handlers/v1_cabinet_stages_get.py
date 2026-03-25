from typing import Literal

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Query

from handlers.dependencies.get_current_client_id import get_current_client_id
from services.get_user.exceptions import UserNotFound
from services.get_user.service import GetUserService
from usecases.get_document_user_status.usecase import GetDocumentUserStatusUseCase
from usecases.get_stages_with_reviewer_and_docs.usecase import GetStagesWithReviewerAndDocsUseCase
from .dtos.helper import openapi_responses
from .dtos.v1_stages_list_get import (
    DocumentGetResponse,
    StageReviewerUserGetResponse,
    StageSummaryGetResponse,
    UserPreview,
    V1_STAGES_LIST_GET_RESPONSE200,
    V1_STAGES_LIST_GET_RESPONSE401,
    V1StageWithReviewerAndDocsGetResponse,
)


router = APIRouter()

@router.get(
    "/v1/cabinet/stages",
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
    get_document_user_status_uc: FromDishka[GetDocumentUserStatusUseCase],
    get_user_service: FromDishka[GetUserService],
    user_id: str = Depends(get_current_client_id),
    roles: list[Literal['author', 'reviewer']] | None = Query(default=None),
    review_statuses: list[Literal['accepted', 'declined']] | None = Query(default=None),
    categories: list[str] | None = Query(default=None),
    doc_statuses: list[
        Literal['new_comment', 'not_viewed', 'viewed', 'waiting', 'action_required', 'sent']
    ] | None = Query(default=None),
) -> list[V1StageWithReviewerAndDocsGetResponse]:
    uid = int(user_id)

    stages = await get_stages_with_reviewer_and_docs_uc.execute(
        author_id=uid,
        roles=roles,
        review_statuses=review_statuses,
        categories=categories,
        doc_statuses=doc_statuses,
    )
    return [
        V1StageWithReviewerAndDocsGetResponse(
            stage=StageSummaryGetResponse(
                stage_id=row.stage.stage_id,
                next_stage=row.stage.next_stage,
                title=row.stage.title,
            ),
            docs=[
                DocumentGetResponse(
                    doc_id=d.doc_id,
                    title=d.title,
                    description=d.description,
                    authors=await _authors_as_preview(get_user_service, d.authors),
                    created_at=d.created_at or "",
                    modified_at=d.modified_at or "",
                    status=await get_document_user_status_uc.status_for_user(d.doc_id, uid)
                    if d.doc_id is not None
                    else None,
                )
                for d in row.docs
            ],
            reviewers=[
                StageReviewerUserGetResponse(
                    user_id=u.user_id,
                    fio=u.fio,
                )
                for u in row.reviewers
            ],
        )
        for row in stages
    ]

async def _authors_as_preview(get_user_service: GetUserService, author_ids: list[int]) -> list[UserPreview]:
    out: list[UserPreview] = []
    for aid in author_ids:
        try:
            u = await get_user_service.execute(aid)
        except UserNotFound:
            out.append(UserPreview(id=aid, fio=""))
        else:
            out.append(UserPreview(id=aid, fio=u.fio))
    return out
