from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException

from handlers.dependencies.get_current_client_id import get_current_client_id
from services.get_pdf_document.exceptions import DocumentNotFound
from usecases.get_document_detail.usecase import GetDocumentDetailUseCase
from .dtos.helper import openapi_responses
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
    _: str = Depends(get_current_client_id),
) -> V1CabinetDocumentGetResponse:
    try:
        detail = await get_document_detail_uc.execute(doc_id)
    except DocumentNotFound as err_not_found:
        raise HTTPException(status_code=404, detail=str(err_not_found)) from err_not_found

    return V1CabinetDocumentGetResponse(
        document=V1CabinetDocumentGetDocumentResponse(
            title=detail.document.title,
            description=detail.document.description,
            file=detail.document.file,
            authors=detail.document.authors,
            stage_id=detail.document.stage_id,
            created_at=str(detail.document.created_at),
            modified_at=str(detail.document.modified_at),
            pdf_file=detail.document.pdf_file,
        ),
        reviews=[
            V1CabinetDocumentGetReviewResponse(
                stage_id=i.stage_id,
                doc_id=i.doc_id,
                user_id=i.user_id,
                is_aproved=i.is_aproved,
                is_viewed=i.is_viewed,
            )
            for i in detail.reviews
        ],
    )
