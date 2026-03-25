from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from handlers.dependencies.get_current_client_id import get_current_client_id
from services.generate_reviews_pdf import GenerateReviewsPdfService


router = APIRouter()


@router.post("/v1/cabinet/reviews/pdf")
@inject
async def cabinet_reviews_pdf(
    generate_reviews_pdf_service: FromDishka[GenerateReviewsPdfService],
    _: str = Depends(get_current_client_id),
) -> Response:
    try:
        pdf_content = generate_reviews_pdf_service.execute()
    except RuntimeError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err),
        ) from err

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="reviews.pdf"'},
    )
