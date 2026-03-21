from fastapi import APIRouter, Form, HTTPException
from dishka.integrations.fastapi import FromDishka, inject

from usecases.issue_token import IssueTokenUseCase

router = APIRouter()


@router.post("/oauth/token")
@inject
async def token(
    use_case: FromDishka[IssueTokenUseCase],
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    scope: str = Form("")
):
    if grant_type != "client_credentials":
        raise HTTPException(status_code=400, detail="unsupported_grant_type")

    try:
        token = await use_case.execute(client_id, client_secret, scope)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "access_token": token.value,
        "token_type": "bearer",
        "expires_in": 900,
        "scope": token.scope,
    }