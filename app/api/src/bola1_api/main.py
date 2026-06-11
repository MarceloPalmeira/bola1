from fastapi import FastAPI

from bola1_api.api.v1.router import api_router
from bola1_api.core.config import settings
from bola1_api.core.cors import setup_cors

app = FastAPI(title=settings.app_name)
setup_cors(app)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
