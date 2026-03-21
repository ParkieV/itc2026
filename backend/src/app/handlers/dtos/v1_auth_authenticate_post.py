from pydantic import BaseModel


class V1AuthAuthenticatePostResponse(BaseModel):
    access_token: str
    token_type: str