import mimetypes
from pathlib import Path

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException, Query, status
from starlette.responses import FileResponse

from repositories.inmemory_document_files_repo import InMemoryDocumentFilesRepository
from .dependencies.get_current_client_id import get_current_client_id
from .dtos.helper import openapi_responses
from .dtos.v1_cabinet_document_pdf_file_get import (
    V1_CABINET_DOCUMENT_PDF_FILE_GET_RESPONSE200,
    V1_CABINET_DOCUMENT_PDF_FILE_GET_RESPONSE403,
    V1_CABINET_DOCUMENT_PDF_FILE_GET_RESPONSE404,
)
from services.get_pdf_document.exceptions import DocumentNotFound
from services.get_pdf_document.exceptions import DocumentNotAllowed
from services.get_pdf_document.service import GetPdfDocumentService


router = APIRouter()


@router.get(
    "/v1/cabinet/document/pdf_file",
    responses=openapi_responses(
        {
            200: V1_CABINET_DOCUMENT_PDF_FILE_GET_RESPONSE200,
            403: V1_CABINET_DOCUMENT_PDF_FILE_GET_RESPONSE403,
            404: V1_CABINET_DOCUMENT_PDF_FILE_GET_RESPONSE404,
        }
    ),
)
@inject
async def cabinet_document_pdf_file(
    get_document_service: FromDishka[GetPdfDocumentService],
    document_files_repo: FromDishka[InMemoryDocumentFilesRepository],
    document_id: int = Query(),
    _: str = Depends(get_current_client_id),
) -> FileResponse:
    try:
        document = await get_document_service.execute(document_id)
    except DocumentNotFound as err_not_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err_not_found)) from err_not_found
    except DocumentNotAllowed as err_not_allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err_not_allowed)) from err_not_allowed

    if document.pdf_file_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document has no pdf file id",
        )

    paths = document_files_repo.get_paths(document.pdf_file_id)
    pdf_file_path = None if paths is None else paths.get("pdf_file_path")
    if not pdf_file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document has no pdf file path",
        )

    path = Path(pdf_file_path)
    if not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found on disk",
        )

    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return FileResponse(path, media_type=media_type, filename=path.name)
