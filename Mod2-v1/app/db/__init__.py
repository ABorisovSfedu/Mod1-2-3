from __future__ import annotations

import os
from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.settings import settings
from app.models import Base  # ensure models are imported so metadata is populated


def _normalized_db_url(url: Optional[str]) -> str:
    """Convert sync sqlite URL to async driver if needed."""
    raw = url or "sqlite:////app/data/mod2.db"
    if raw.startswith("sqlite+aiosqlite:"):
        return raw
    if raw.startswith("sqlite:"):
        return raw.replace("sqlite:", "sqlite+aiosqlite:", 1)
    return raw


DB_URL = _normalized_db_url(getattr(settings, "db_url", None))

# Ensure directory exists for SQLite file paths like sqlite+aiosqlite:////app/data/mod2.db
if DB_URL.startswith("sqlite+aiosqlite:") and ":memory:" not in DB_URL:
    try:
        # Extract filesystem path after scheme, strip leading slashes appropriately
        path_part = DB_URL.split(":", 1)[1]
        # path_part looks like //[/]app/data/mod2.db → normalize
        path = path_part.lstrip("/")
        dir_path = os.path.dirname("/" + path)
        os.makedirs(dir_path, exist_ok=True)
    except Exception:
        pass


engine = create_async_engine(DB_URL, echo=False, future=True)
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Create tables if they do not exist (simple bootstrap without Alembic)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



