import uvicorn
from bootstrap import bootstrap


if __name__ == "__main__":
    app = bootstrap()
    uvicorn.run(app, host="0.0.0.0", port=8000)