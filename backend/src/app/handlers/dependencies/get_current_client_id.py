from fastapi import Depends, HTTPException, status
from handlers.dependencies.validate_jwt_token import validate_jwt_token

async def get_current_client_id(
    token_payload: dict = Depends(validate_jwt_token),
) -> str:
    print(type(token_payload))
    client_id = token_payload.get("sub")
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_token",
        )
    return client_id