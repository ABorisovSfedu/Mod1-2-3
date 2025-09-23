from __future__ import annotations
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, Header, HTTPException, status

# ВАЛИДАЦИЯ по JSON-схемам
from app.utils.schemas import chunk_validator, final_validator

# Подпись HMAC-SHA256
from app.utils.security import verify_hmac_sha256

# Настройки (ingest_secret, stream_preview и т.п.)
try:
    from app.settings import settings  # type: ignore
except Exception:
    from app.config import settings  # type: ignore
from app.services.ingest_service import process_chunk, process_final
from app.services.idempotency import seen_before
from app.services.webhooks import upsert_webhook, get_secret_for_session
from app.services.tracing import log_event 

router = APIRouter(prefix="/v2")


@router.post("/webhooks/register")
async def register_webhook(payload: Dict[str, Any]):
    """
    Регистрация вебхука/секрета для конкретной session_id.
    Ожидаем payload:
      {
        "session_id": "<id>",             # обязательно
        "url_chunk": "http://.../chunk",  # опционально
        "url_final": "http://.../full",   # опционально
        "secret": "<per-session-secret>"  # опционально
      }
    """
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid JSON")

    sid = payload.get("session_id")
    if not sid or not isinstance(sid, str):
        raise HTTPException(status_code=400, detail="session_id required")

    await upsert_webhook(payload)
    return {"status": "ok"}


@router.post("/ingest/chunk")
async def ingest_chunk(
    request: Request,
    x_signature: Optional[str] = Header(default=None, alias="X-Signature"),
    idem_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    x_request_id: Optional[str] = Header(default=None, alias="X-Request-Id"),
):
    """
    Приём чанка. Проверяем:
      1) подпись X-Signature (HMAC-SHA256 на основе raw body и секрета),
         секрет берём из таблицы webhooks по session_id, если есть, иначе — settings.ingest_secret
      2) валидируем JSON по contracts/chunk.json
      3) идемпотентность по Idempotency-Key
    """
    raw = await request.body()

    # сначала читаем JSON, чтобы достать session_id (для подбора секрета)
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    sid = data.get("session_id") if isinstance(data, dict) else None
    per_session_secret = await get_secret_for_session(sid) if sid else None
    use_secret = per_session_secret or settings.ingest_secret

    if not verify_hmac_sha256(use_secret, raw, x_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad signature")

    # валидация по схеме chunk.json
    errors = sorted(e.message for e in chunk_validator.iter_errors(data))
    if errors:
        raise HTTPException(status_code=400, detail={"schema_errors": errors})

    # идемпотентность
    if idem_key and await seen_before(idem_key):
        log_event(
            "chunk_received",
            service="module2",
            session_id=data.get("session_id"),
            seq=data.get("seq"),
            status="idempotent",
            request_id=x_request_id,
        )
        return {"status": "ok", "idempotent": True}

    log_event(
        "chunk_received",
        service="module2",
        session_id=data.get("session_id"),
        seq=data.get("seq"),
        status="ok",
        request_id=x_request_id,
    )

    # обработка
    await process_chunk(data, idem_key)

    return {"status": "ok"}


@router.post("/ingest/full")
async def ingest_full(
    request: Request,
    x_signature: Optional[str] = Header(default=None, alias="X-Signature"),
    idem_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    x_request_id: Optional[str] = Header(default=None, alias="X-Request-Id"),
):
    """
    Приём финального результата. Проверяем подпись, валидируем JSON и обрабатываем.
    """
    raw = await request.body()

    # читаем JSON, чтобы достать session_id (для подбора секрета)
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    sid = data.get("session_id") if isinstance(data, dict) else None
    per_session_secret = await get_secret_for_session(sid) if sid else None
    use_secret = per_session_secret or settings.ingest_secret

    if not verify_hmac_sha256(use_secret, raw, x_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad signature")

    # валидация по схеме final.json
    errors = sorted(e.message for e in final_validator.iter_errors(data))
    if errors:
        raise HTTPException(status_code=400, detail={"schema_errors": errors})

    # идемпотентность
    if idem_key and await seen_before(idem_key):
        log_event(
            "final_received",
            service="module2",
            session_id=data.get("session_id"),
            seq=None,
            status="idempotent",
            request_id=x_request_id,
        )
        return {"status": "ok", "idempotent": True}

    log_event(
        "final_received",
        service="module2",
        session_id=data.get("session_id"),
        seq=None,
        status="ok",
        request_id=x_request_id,
    )

    # обработка
    await process_final(data, idem_key)

    return {"status": "ok"}
