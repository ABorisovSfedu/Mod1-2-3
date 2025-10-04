from fastapi import APIRouter
import os
from datetime import datetime

router = APIRouter(tags=["health"])


@router.get("/healthz")
def health_check():
    """Enhanced health check endpoint for Mod3-v1 Visual Mapping service"""
    # Read ENV settings without breaking existing configuration
    host = os.getenv("MOD3_HOST", "0.0.0.0")
    port = int(os.getenv("MOD3_PORT", "9001"))
    require_props = os.getenv("M3_REQUIRE_PROPS", "true").lower() == "true"
    names_normalize = os.getenv("M3_NAMES_NORMALIZE", "true").lower() == "true"
    dedup_by_component = os.getenv("M3_DEDUP_BY_COMPONENT", "true").lower() == "true"
    at_least_one_main = os.getenv("M3_AT_LEAST_ONE_MAIN", "true").lower() == "true"
    fallback_sections = os.getenv("M3_FALLBACK_SECTIONS", "true").lower() == "true"
    max_matches = int(os.getenv("M3_MAX_MATCHES", "6"))
    
    return {
        "status": "ok",
        "service": "Mod3-v1 - Visual Elements Mapping",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "host": host,
        "port": port,
        "database_url": os.getenv("DATABASE_URL", "sqlite:///./mod3.db"),
        "feature_flags": {
            "require_props": require_props,
            "names_normalize": names_normalize,
            "dedup_by_component": dedup_by_component,
            "at_least_one_main": at_least_one_main,
            "fallback_sections": fallback_sections,
            "max_matches": max_matches
        },
        "timestamp": datetime.utcnow().isoformat()
    }

