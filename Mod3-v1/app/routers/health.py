from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthz")
def health_check():
    """Проверка состояния сервиса"""
    return {
        "status": "ok",
        "service": "Mod3-v1 - Visual Elements Mapping",
        "version": "1.0.0"
    }

