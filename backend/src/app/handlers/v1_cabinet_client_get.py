from fastapi import APIRouter, Depends
from backend.src.app import Client
from handlers.dependencies.get_current_client_id import get_current_client_id

router = APIRouter(prefix="/v1/cabinet")

@router.get("/client")
async def cabinet_client(client: Client = Depends(get_current_client_id)):
    return {
        "client_id": client.client_id,
        "scopes": list(client.scopes),
        "redirect_uris": list(client.redirect_uris),
    }