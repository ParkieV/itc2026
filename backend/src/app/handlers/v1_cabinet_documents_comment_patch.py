from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException

from handlers.dependencies.get_current_client_id import get_current_client_id
from services.comment_exceptions import CommentNotFound
from services.get_pdf_document.exceptions import DocumentNotFound
from services.patch_comment.service import PatchCommentService
from .dtos.helper import openapi_responses
from .dtos.v1_cabinet_documents_comment_patch import (
    V1_CABINET_DOCUMENTS_COMMENT_PATCH_RESPONSE200,
    V1_CABINET_DOCUMENTS_COMMENT_PATCH_RESPONSE401,
    V1_CABINET_DOCUMENTS_COMMENT_PATCH_RESPONSE404,
    V1CabinetDocumentsCommentPatchRequest,
)
from .dtos.v1_cabinett_document_comments import V1CabinettDocumentCommentResponse

router = APIRouter()


def _comment_to_response(c) -> V1CabinettDocumentCommentResponse:
    return V1CabinettDocumentCommentResponse(
        comment_id=c.comment_id,
        doc_id=c.doc_id,
        stage_id=c.stage_id,
        user_id=c.user_id,
        reply_to=c.reply_to,
        subject=c.subject,
        content=c.content,
        xfdf=c.xfdf,
        status=c.status,
        is_viewed=c.is_viewed,
        created_at=str(c.created_at),
    )


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
    _: str = Depends(get_current_client_id),
) -> V1CabinettDocumentCommentResponse:
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
    return _comment_to_response(updated)
