from .entities.client import Client
from repositories.client_inmemory_repo import AsyncInMemoryClientRepository

class ClientService:
    def __init__(self, client_repo: AsyncInMemoryClientRepository):
        self.client_repo = client_repo

    async def get_client_by_id(self, client_id: str) -> Client | None:
        return await self.client_repo.get_by_id(client_id)