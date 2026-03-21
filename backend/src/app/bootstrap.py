from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka

from di.container import container
from handlers.oauth_token_post import router

def bootstrap() -> FastAPI:
    app = FastAPI(title="OAuth2 Service")
    setup_dishka(container, app)
    app.include_router(router)
    return app