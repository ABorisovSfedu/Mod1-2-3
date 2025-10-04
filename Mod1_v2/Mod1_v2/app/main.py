from __future__ import annotations
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .utils.logging import setup_json_logging
from .db import init_db
from .config import settings
from .routers import health, hooks, transcribe, stream, session

setup_json_logging(settings.app.log_level)
init_db()

app = FastAPI(title="ASR + Chunker (RU) — MVP")

# Настройка CORS для разрешения запросов с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(hooks.router)
app.include_router(transcribe.router)
app.include_router(session.router)
app.include_router(stream.router)

app.mount("/", StaticFiles(directory="public", html=True), name="public")