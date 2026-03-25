from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException

from handlers.dependencies.get_current_client_id import get_current_client_id
from services.get_pdf_document.exceptions import DocumentNotFound
from services.get_user.exceptions import UserNotFound
from services.get_user.service import GetUserService
from usecases.get_document_detail.usecase import GetDocumentDetailUseCase
from usecases.get_document_user_status.usecase import GetDocumentUserStatusUseCase
from .dtos.comment_author_preview import CommentAuthorPreview
from .dtos.helper import openapi_responses
from .dtos.v1_cabinet_document_comments_get import V1CabinetDocumentCommentResponse
from .dtos.v1_cabinet_document_get import (
    V1_CABINET_DOCUMENT_GET_RESPONSE200,
    V1_CABINET_DOCUMENT_GET_RESPONSE401,
    V1_CABINET_DOCUMENT_GET_RESPONSE404,
    V1CabinetDocumentGetDocumentResponse,
    V1CabinetDocumentGetReviewResponse,
    V1CabinetDocumentGetResponse,
)

router = APIRouter()


@router.get(
    "/v1/cabinet/document/{doc_id}",
    responses=openapi_responses(
        {
            200: V1_CABINET_DOCUMENT_GET_RESPONSE200,
            401: V1_CABINET_DOCUMENT_GET_RESPONSE401,
            404: V1_CABINET_DOCUMENT_GET_RESPONSE404,
        }
    ),
)
@inject
async def cabinet_document_get(
    doc_id: int,
    get_document_detail_uc: FromDishka[GetDocumentDetailUseCase],
    get_document_user_status_uc: FromDishka[GetDocumentUserStatusUseCase],
    get_user_service: FromDishka[GetUserService],
    user_id: str = Depends(get_current_client_id),
) -> V1CabinetDocumentGetResponse:
    try:
        detail = await get_document_detail_uc.execute(doc_id)
    except DocumentNotFound as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found)) from err_not_found

    status = await get_document_user_status_uc.status_for_user(doc_id, int(user_id))

    comments_out: list[V1CabinetDocumentCommentResponse] = []
    for c in detail.comments:
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
        comments_out.append(
            V1CabinetDocumentCommentResponse(
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
        )

    return V1CabinetDocumentGetResponse(
        document=V1CabinetDocumentGetDocumentResponse(
            title=detail.document.title,
            description=detail.document.description,
            file_id=detail.document.file_id,
            authors=detail.document.authors,
            stage_id=detail.document.stage_id,
            created_at=detail.document.created_at or "",
            modified_at=detail.document.modified_at or "",
            pdf_file_id=detail.document.pdf_file_id,
            status=status,
        ),
        reviews=[
            V1CabinetDocumentGetReviewResponse(
                stage_id=i.stage_id,
                doc_id=i.doc_id,
                user_id=i.user_id,
                status=i.status,
                is_viewed=i.is_viewed,
            )
            for i in detail.reviews
        ],
        comments=comments_out,
    )
