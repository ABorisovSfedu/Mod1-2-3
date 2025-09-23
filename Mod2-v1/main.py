from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from config.settings import settings
from app.routers.ingest import router as ingest_router
from app.routers.vocab import router as vocab_router
from app.routers.debug import router as debug_router
from app.routers.session import router as session_router
from app.nlp.pipeline import preload_ru
from app.routers import ingest
from app.health import router as health_router

app = FastAPI(title=settings.app_name)
app.include_router(ingest.router)
app.include_router(health_router)

@app.on_event("startup")
async def _startup():
    preload_ru()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"status": "error", "message": "Invalid request payload", "errors": exc.errors()},
    )

@app.get("/healthz", tags=["health"])
def healthz():
    return {"status": "ok"}

app.include_router(ingest_router)
app.include_router(vocab_router)
app.include_router(debug_router)
app.include_router(session_router)
