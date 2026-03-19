from .models.client import ClientModel

class AsyncInMemoryClientRepository:
    def __init__(self):
        self.clients = {
            "client-1": ClientModel(
                client_id="client-1",
                client_secret="secret",
                scopes={"read", "write"},
                redirect_uris={"https://example.com/callback"},
            )
        }

    async def get_by_id(self, client_id: str) -> ClientModel | None:
        return self.clients.get(client_id)