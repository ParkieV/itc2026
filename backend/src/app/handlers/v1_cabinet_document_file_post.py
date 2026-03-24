from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status, File
from dishka import FromDishka
from dishka.integrations.fastapi import inject

from entities import Document
from .dtos.v1_cabinet_document_file_post import (
    V1CabinetDocumentFilePostResponse200,
    V1CabinetDocumentFilePostResponse400,
    V1CabinetDocumentFilePostResponse403,
    V1CabinetDocumentFilePostResponse404,
)
from .dependencies.get_current_client_id import get_current_client_id
from .dtos.helper import openapi_responses
from usecases.create_document_file.usecase import CreateDocumentFileUseCase
from services.get_origin_document.service import GetOriginDocumentService
from services.get_origin_document.exceptions import DocumentNotAllowed
from services.get_origin_document.exceptions import DocumentNotFound
from services.add_origin_document_file.exceptions import FileExists
from services.save_pdf_document_file.exceptions import (
    OriginFileNotFound,
    PdfConversionFailed,
    PdfFileExists,
    UnsupportedOriginFormat,
)
from services.add_origin_document_file.exceptions import InvalidDocumentFormat
from services.add_document.exceptions import InvalidAuthorId


router = APIRouter()

@router.post(
    "/v1/cabinet/document/file",
    responses=openapi_responses(
        {
            200: V1CabinetDocumentFilePostResponse200,
            400: V1CabinetDocumentFilePostResponse400,
            403: V1CabinetDocumentFilePostResponse403,
            404: V1CabinetDocumentFilePostResponse404,
        }
    ),
)
@inject
async def create_cabinet_document_file(
    create_document_file_uc: FromDishka[CreateDocumentFileUseCase],
    get_origin_document_service: FromDishka[GetOriginDocumentService],
    title: str = Form(...),
    description: str = Form(...),
    authors: list[int] = Form(...),
    file: UploadFile = File(...),
    client_id: str = Depends(get_current_client_id),
) -> V1CabinetDocumentFilePostResponse200:
    normalized_authors = authors
    current_client_id = int(client_id)
    if current_client_id not in normalized_authors:
        normalized_authors.append(current_client_id)

    try:
        document_id = await create_document_file_uc.execute(
            document=Document(
                title=title,
                description=description,
                authors=normalized_authors,
                stage_id=1,
            ),
            upload_file=file,
            creator_user_id=current_client_id,
        )
    except (
        InvalidDocumentFormat,
        FileExists,
        PdfFileExists,
        PdfConversionFailed,
        OriginFileNotFound,
        UnsupportedOriginFormat,
    ) as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)) from err
    except (InvalidAuthorId, DocumentNotAllowed) as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err)) from err
    except DocumentNotFound as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err)) from err

    created_document = await get_origin_document_service.execute(document_id, int(client_id))
    return V1CabinetDocumentFilePostResponse200(
        document_id=document_id,
        file_id=created_document.file_id or 0,
        pdf_file_id=created_document.pdf_file_id or 0,
    )
