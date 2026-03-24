from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException

from handlers.dependencies.get_current_client_id import get_current_client_id
from services.get_comments_by_doc.service import GetCommentsByDocService
from services.get_pdf_document.exceptions import DocumentNotFound
from services.get_stage_by_id.exceptions import StageNotFound
from .dtos.helper import openapi_responses
from .dtos.v1_cabinet_document_comments_all_get import (
    V1_CABINET_DOCUMENT_COMMENTS_ALL_GET_RESPONSE200,
    V1_CABINET_DOCUMENT_COMMENTS_ALL_GET_RESPONSE401,
    V1_CABINET_DOCUMENT_COMMENTS_ALL_GET_RESPONSE404,
    V1CabinetDocumentCommentAllResponse,
)


router = APIRouter()

@router.get(
    "/v1/cabinet/document/{doc_id}/comments/all",
    responses=openapi_responses(
        {
            200: V1_CABINET_DOCUMENT_COMMENTS_ALL_GET_RESPONSE200,
            401: V1_CABINET_DOCUMENT_COMMENTS_ALL_GET_RESPONSE401,
            404: V1_CABINET_DOCUMENT_COMMENTS_ALL_GET_RESPONSE404,
        }
    ),
)
@inject
async def get_document_comments_all(
    doc_id: int,
    get_comments_by_doc_service: FromDishka[GetCommentsByDocService],
    _: str = Depends(get_current_client_id),
) -> list[V1CabinetDocumentCommentAllResponse]:
    try:
        comments = await get_comments_by_doc_service.execute(doc_id)
    except (DocumentNotFound, StageNotFound) as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found)) from err_not_found

    return [_comment_to_response(i) for i in comments]

def _comment_to_response(i) -> V1CabinetDocumentCommentAllResponse:
    return V1CabinetDocumentCommentAllResponse(
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
