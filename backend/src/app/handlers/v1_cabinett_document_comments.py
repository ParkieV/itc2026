from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException, Query

from handlers.dependencies.get_current_client_id import get_current_client_id
from services.comment_exceptions import CommentNotFound
from services.create_comment.service import CreateCommentService
from services.get_comments_by_doc.service import GetCommentsByDocService
from services.get_comments_by_doc_and_stage.service import GetCommentsByDocAndStageService
from services.get_pdf_document.exceptions import DocumentNotFound
from services.get_stage_by_id.exceptions import StageNotFound
from services.get_user.exceptions import UserNotFound
from .dtos.helper import openapi_responses
from .dtos.v1_cabinett_document_comments import (
    V1_CABINETT_DOCUMENT_COMMENTS_GET_RESPONSE200,
    V1_CABINETT_DOCUMENT_COMMENTS_POST_RESPONSE200,
    V1_CABINETT_DOCUMENT_COMMENTS_RESPONSE401,
    V1_CABINETT_DOCUMENT_COMMENTS_RESPONSE404,
    V1CabinettDocumentCommentResponse,
    V1CabinettDocumentCreateCommentRequest,
)

router = APIRouter()


def _comment_to_response(i) -> V1CabinettDocumentCommentResponse:
    return V1CabinettDocumentCommentResponse(
        comment_id=i.comment_id,
        doc_id=i.doc_id,
        stage_id=i.stage_id,
        user_id=i.user_id,
        reply_to=i.reply_to,
        subject=i.subject,
        content=i.content,
        xfdf=i.xfdf,
        status=i.status,
        is_viewed=i.is_viewed,
        created_at=i.created_at,
    )


@router.post(
    "/v1/cabinett/document/{doc_id}/comments",
    responses=openapi_responses(
        {
            200: V1_CABINETT_DOCUMENT_COMMENTS_POST_RESPONSE200,
            401: V1_CABINETT_DOCUMENT_COMMENTS_RESPONSE401,
            404: V1_CABINETT_DOCUMENT_COMMENTS_RESPONSE404,
        }
    ),
)
@inject
async def create_document_comment(
    doc_id: int,
    request: V1CabinettDocumentCreateCommentRequest,
    create_comment_service: FromDishka[CreateCommentService],
    user_id: str = Depends(get_current_client_id),
) -> None:
    try:
        await create_comment_service.execute(
            doc_id=doc_id,
            stage_id=request.stage_id,
            user_id=int(user_id),
            subject=request.subject,
            content=request.content,
            xfdf=request.xfdf,
            reply_to=request.reply_to,
        )
    except (DocumentNotFound, StageNotFound, UserNotFound, CommentNotFound) as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found)) from err_not_found


@router.get(
    "/v1/cabinett/document/{doc_id}/comments",
    responses=openapi_responses(
        {
            200: V1_CABINETT_DOCUMENT_COMMENTS_GET_RESPONSE200,
            401: V1_CABINETT_DOCUMENT_COMMENTS_RESPONSE401,
            404: V1_CABINETT_DOCUMENT_COMMENTS_RESPONSE404,
        }
    ),
)
@inject
async def get_document_comments(
    doc_id: int,
    get_comments_by_doc_and_stage_service: FromDishka[GetCommentsByDocAndStageService],
    stage_id: int = Query(),
    _: str = Depends(get_current_client_id),
) -> list[V1CabinettDocumentCommentResponse]:
    try:
        comments = await get_comments_by_doc_and_stage_service.execute(doc_id, stage_id)
    except (DocumentNotFound, StageNotFound) as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found)) from err_not_found

    return [_comment_to_response(i) for i in comments]


@router.get(
    "/v1/cabinett/document/{doc_id}/comments/all",
    responses=openapi_responses(
        {
            200: V1_CABINETT_DOCUMENT_COMMENTS_GET_RESPONSE200,
            401: V1_CABINETT_DOCUMENT_COMMENTS_RESPONSE401,
            404: V1_CABINETT_DOCUMENT_COMMENTS_RESPONSE404,
        }
    ),
)
@inject
async def get_document_comments_all(
    doc_id: int,
    get_comments_by_doc_service: FromDishka[GetCommentsByDocService],
    _: str = Depends(get_current_client_id),
) -> list[V1CabinettDocumentCommentResponse]:
    try:
        comments = await get_comments_by_doc_service.execute(doc_id)
    except (DocumentNotFound, StageNotFound) as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found)) from err_not_found

    return [_comment_to_response(i) for i in comments]
