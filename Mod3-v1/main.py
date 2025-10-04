from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from app.database import init_db
from app.routers import health_router, mapping_router, vocab_router

# Создаем приложение
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Микросервис для сопоставления NLP результатов с визуальными элементами"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(health_router)
app.include_router(mapping_router)
app.include_router(vocab_router)


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    # Инициализируем базу данных
    init_db()


@app.get("/")
def root():
    """Корневой эндпоинт"""
    return {
        "message": "Mod3-v1 - Visual Elements Mapping Service",
        "version": settings.app_version,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )

