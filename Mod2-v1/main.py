from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from app.routers.ingest import router as ingest_router
from app.routers.vocab import router as vocab_router
from app.routers.debug import router as debug_router
from app.routers.session import router as session_router
from app.nlp.pipeline import preload_ru
from app.routers import ingest
from app.health import router as health_router
from app.db import init_db

app = FastAPI(title=settings.app_name)

# Настройка CORS для разрешения запросов с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(health_router)
app.include_router(session_router)
app.include_router(vocab_router)
app.include_router(debug_router)

@app.on_event("startup")
async def _startup():
    # Не блокируем старт приложения на загрузке моделей Stanza.
    # Попробуем прогреть в фоне, а если не получится — просто продолжим.
    try:
        import threading
        threading.Thread(target=preload_ru, daemon=True).start()
    except Exception:
        # Логирование можно добавить позже; не мешаем запуску
        pass
    # Инициализируем БД (создаём таблицы при первом запуске)
    try:
        await init_db()
    except Exception:
        # Не валим приложение, если таблицы уже есть или окружение без БД
        pass

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"status": "error", "message": "Invalid request payload", "errors": exc.errors()},
    )

@app.get("/healthz", tags=["health"])
def healthz():
    return {"status": "ok"}

