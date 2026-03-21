from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka
from starlette.middleware.cors import CORSMiddleware

from di.container import container
from handlers import router


def bootstrap() -> FastAPI:
    app = FastAPI(title="Backend service")
    setup_dishka(container, app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )

    app.include_router(router)
    return app