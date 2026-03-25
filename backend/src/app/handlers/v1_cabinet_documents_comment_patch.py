from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException

from handlers.dependencies.get_current_client_id import get_current_client_id
from services.comment_exceptions import CommentNotFound
from services.get_pdf_document.exceptions import DocumentNotFound
from services.get_user.exceptions import UserNotFound
from services.get_user.service import GetUserService
from services.patch_comment.service import PatchCommentService
from .dtos.helper import openapi_responses
from .dtos.v1_cabinet_documents_comment_patch import (
    V1_CABINET_DOCUMENTS_COMMENT_PATCH_RESPONSE200,
    V1_CABINET_DOCUMENTS_COMMENT_PATCH_RESPONSE401,
    V1_CABINET_DOCUMENTS_COMMENT_PATCH_RESPONSE404,
    V1CabinetDocumentsCommentPatchRequest,
)
from .dtos.v1_cabinet_documents_comment_patch import V1CabinetDocumentsCommentPatchResponse
from .dtos.comment_author_preview import CommentAuthorPreview

router = APIRouter()


@router.patch(
    "/v1/cabinet/documents/{doc_id}/comments/{comment_id}",
    responses=openapi_responses(
        {
            200: V1_CABINET_DOCUMENTS_COMMENT_PATCH_RESPONSE200,
            401: V1_CABINET_DOCUMENTS_COMMENT_PATCH_RESPONSE401,
            404: V1_CABINET_DOCUMENTS_COMMENT_PATCH_RESPONSE404,
        }
    ),
)
@inject
async def patch_document_comment(
    doc_id: int,
    comment_id: int,
    request: V1CabinetDocumentsCommentPatchRequest,
    patch_comment_service: FromDishka[PatchCommentService],
    get_user_service: FromDishka[GetUserService],
    _: str = Depends(get_current_client_id),
) -> V1CabinetDocumentsCommentPatchResponse:
    try:
        updated = await patch_comment_service.execute(
            doc_id,
            comment_id,
            is_viewed=request.is_viewed,
            status=request.status,
        )
    except DocumentNotFound as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found)) from err_not_found
    except CommentNotFound as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found)) from err_not_found
    return await _comment_to_response(updated, get_user_service)


async def _comment_to_response(c, get_user_service: GetUserService) -> V1CabinetDocumentsCommentPatchResponse:
    try:
        u = await get_user_service.execute(c.user_id)
        fio = u.fio
        organization = u.organization
        phone = u.phone
        email = u.email
    except UserNotFound:
        fio = ""
        organization = ""
        phone = ""
        email = ""
    return V1CabinetDocumentsCommentPatchResponse(
        comment_id=c.comment_id,
        doc_id=c.doc_id,
        stage_id=c.stage_id,
        author=CommentAuthorPreview(user_id=c.user_id, fio=fio, organization=organization, phone=phone, email=email),
        reply_to=c.reply_to,
        remark=c.remark,
        proposal=c.proposal,
        justification=c.justification,
        developer_response=c.developer_response,
        xfdf=c.xfdf,
        status=c.status,
        is_viewed=c.is_viewed,
        created_at=c.created_at,
    )