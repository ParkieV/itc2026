from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException

from handlers.dependencies.get_current_client_id import get_current_client_id
from services.get_comments_by_doc.service import GetCommentsByDocService
from services.get_pdf_document.exceptions import DocumentNotFound
from services.get_stage_by_id.exceptions import StageNotFound
from services.get_user.exceptions import UserNotFound
from services.get_user.service import GetUserService
from .dtos.comment_author_preview import CommentAuthorPreview
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
    get_user_service: FromDishka[GetUserService],
    _: str = Depends(get_current_client_id),
) -> list[V1CabinetDocumentCommentAllResponse]:
    try:
        comments = await get_comments_by_doc_service.execute(doc_id)
    except (DocumentNotFound, StageNotFound) as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found)) from err_not_found

    out: list[V1CabinetDocumentCommentAllResponse] = []
    for c in comments:
        out.append(await _comment_to_response(c, get_user_service))
    return out


async def _comment_to_response(
    c, get_user_service: GetUserService
) -> V1CabinetDocumentCommentAllResponse:
    try:
        u = await get_user_service.execute(c.user_id)
        fio = u.fio
    except UserNotFound:
        fio = ""
    return V1CabinetDocumentCommentAllResponse(
        comment_id=c.comment_id,
        doc_id=c.doc_id,
        stage_id=c.stage_id,
        author=CommentAuthorPreview(user_id=c.user_id, fio=fio),
        reply_to=c.reply_to,
        subject=c.subject,
        content=c.content,
        xfdf=c.xfdf,
        status=c.status,
        is_viewed=c.is_viewed,
        created_at=c.created_at,
    )
