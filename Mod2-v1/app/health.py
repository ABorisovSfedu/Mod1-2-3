from fastapi import APIRouter
from app.settings import settings

router = APIRouter()

@router.get("/healthz")
async def healthz():
    return {
        "status": "ok",
        "stanza_ready": True,     # TODO: реальная проверка
        "model_warm": True,       # TODO: реальная проверка
        "stream_preview": settings.stream_preview,
    }
