import mimetypes
from pathlib import Path

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException, Query, status
from starlette.responses import FileResponse

from repositories.inmemory_document_files_repo import InMemoryDocumentFilesRepository
from services.get_origin_document.exceptions import DocumentNotAllowed, DocumentNotFound
from services.get_origin_document.service import GetOriginDocumentService
from .dependencies.get_current_client_id import get_current_client_id
from .dtos.v1_cabinet_document_file_get import (
    V1_CABINET_DOCUMENT_FILE_GET_RESPONSE200,
    V1_CABINET_DOCUMENT_FILE_GET_RESPONSE403,
    V1_CABINET_DOCUMENT_FILE_GET_RESPONSE404,
)
from .dtos.helper import openapi_responses

router = APIRouter()


@router.get(
    "/v1/cabinet/document/file",
    responses=openapi_responses(
        {
            200: V1_CABINET_DOCUMENT_FILE_GET_RESPONSE200,
            403: V1_CABINET_DOCUMENT_FILE_GET_RESPONSE403,
            404: V1_CABINET_DOCUMENT_FILE_GET_RESPONSE404,
        }
    ),
)
@inject
async def cabinet_document_file(
    get_origin_document_service: FromDishka[GetOriginDocumentService],
    document_files_repo: FromDishka[InMemoryDocumentFilesRepository],
    document_id: int = Query(),
    client_id: str = Depends(get_current_client_id),
) -> FileResponse:
    try:
        document = await get_origin_document_service.execute(document_id, int(client_id))
    except DocumentNotFound as err_not_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err_not_found)) from err_not_found
    except DocumentNotAllowed as err_not_allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err_not_allowed)) from err_not_allowed

    if document.file_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document has no origin file id",
        )

    paths = document_files_repo.get_paths(document.file_id)
    origin_file_path = None if paths is None else paths.get("origin_file_path")
    if not origin_file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document has no origin file path",
        )

    path = Path(origin_file_path)
    if not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk",
        )

    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return FileResponse(path, media_type=media_type, filename=path.name)

