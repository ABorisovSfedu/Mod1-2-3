from .health import router as health_router
from .mapping import router as mapping_router
from .vocab import router as vocab_router

__all__ = [
    "health_router",
    "mapping_router",
    "vocab_router"
]

