from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException

from handlers.dependencies.get_current_client_id import get_current_client_id
from services.comment_exceptions import CommentNotFound
from services.create_comment.service import CreateCommentService
from services.get_pdf_document.exceptions import DocumentNotFound
from services.get_stage_by_id.exceptions import StageNotFound
from services.get_user.exceptions import UserNotFound
from .dtos.helper import openapi_responses
from .dtos.v1_cabinet_document_comments_post import (
    V1_CABINET_DOCUMENT_COMMENTS_POST_RESPONSE200,
    V1_CABINET_DOCUMENT_COMMENTS_POST_RESPONSE401,
    V1_CABINET_DOCUMENT_COMMENTS_POST_RESPONSE404,
    V1CabinetDocumentCreateCommentRequest,
)


router = APIRouter()

@router.post(
    "/v1/cabinet/document/{doc_id}/comments",
    responses=openapi_responses(
        {
            200: V1_CABINET_DOCUMENT_COMMENTS_POST_RESPONSE200,
            401: V1_CABINET_DOCUMENT_COMMENTS_POST_RESPONSE401,
            404: V1_CABINET_DOCUMENT_COMMENTS_POST_RESPONSE404,
        }
    ),
)
@inject
async def create_document_comment(
    doc_id: int,
    request: V1CabinetDocumentCreateCommentRequest,
    create_comment_service: FromDishka[CreateCommentService],
    user_id: str = Depends(get_current_client_id),
) -> None:
    try:
        await create_comment_service.execute(
            doc_id=doc_id,
            stage_id=request.stage_id,
            user_id=int(user_id),
            remark=request.remark,
            proposal=request.proposal,
            justification=request.justification,
            developer_response=request.developer_response,
            xfdf=request.xfdf,
            reply_to=request.reply_to,
        )
    except (DocumentNotFound, StageNotFound, UserNotFound, CommentNotFound) as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found)) from err_not_found
