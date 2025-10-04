from __future__ import annotations
from fastapi import APIRouter
import os
from datetime import datetime

router = APIRouter()

@router.get("/healthz")
async def healthz():
    """Health check endpoint for Mod1_v2 ASR service"""
    # Read ENV settings without breaking existing configuration
    host = os.getenv("MOD1_HOST", "0.0.0.0")
    port = int(os.getenv("MOD1_PORT", "8080"))
    
    return {
        "status": "ok",
        "asr": "ready",
        "service": "Mod1_v2",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "host": host,
        "port": port,
        "timestamp": datetime.utcnow().isoformat()
    }