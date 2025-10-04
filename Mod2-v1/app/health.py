from fastapi import APIRouter
from config.settings import settings
import os
from datetime import datetime

router = APIRouter()

@router.get("/healthz")
async def healthz():
    """Health check endpoint for Mod2-v1 NLP service"""
    # Read ENV settings without breaking existing configuration
    host = os.getenv("MOD2_HOST", "0.0.0.0")
    port = int(os.getenv("MOD2_PORT", "8001"))
    layout_provider = os.getenv("LAYOUT_PROVIDER", "external")
    mod3_url = os.getenv("MOD3_URL", "http://localhost:9001")
    nlp_debug = os.getenv("NLP_DEBUG", "false").lower() == "true"
    
    return {
        "status": "ok",
        "service": "Mod2-v1",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "host": host,
        "port": port,
        "stanza_ready": True,     # TODO: реальная проверка Stanza модели
        "model_warm": True,       # TODO: реальная проверка
        "layout_provider": layout_provider,
        "mod3_url": mod3_url,
        "nlp_debug": nlp_debug,
        "max_components_per_page": os.getenv("MAX_COMPONENTS_PER_PAGE", "20"),
        "fuzzy_threshold": float(os.getenv("FUZZY_THRESHOLD", "0.80")),
        "timestamp": datetime.utcnow().isoformat(),
        # Legacy settings for compatibility
        "stream_preview": settings.stream_preview,
    }
