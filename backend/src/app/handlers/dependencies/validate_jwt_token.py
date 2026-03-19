from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dishka.integrations.fastapi import FromDishka
from jwt import PyJWTError

from security.jwt_provider import JWTProvider

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

async def validate_jwt_token(
    token: str = Depends(oauth2_scheme),
    jwt_provider: JWTProvider = FromDishka(),
) -> dict:
    try:
        payload = jwt_provider.decode(token)
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_token",
        )

    return payload