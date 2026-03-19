import uvicorn
from bootstrap import bootstrap

app = None

if __name__ == "__main__":
    import asyncio

    async def _run():
        global app
        app = await bootstrap()
        uvicorn.run(app, host="0.0.0.0", port=8000)

    asyncio.run(_run())