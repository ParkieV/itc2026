from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dishka.integrations.fastapi import FromDishka, inject
from jwt import PyJWTError

from security.jwt_provider import JWTProvider

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/authenticate")

@inject
async def validate_jwt_token(
        jwt_provider: FromDishka[JWTProvider],
        token: str = Depends(oauth2_scheme),
) -> dict:
    try:
        payload = jwt_provider.decode(token)
    except PyJWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_token",
        )

    return payload