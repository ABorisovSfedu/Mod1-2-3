from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from pydantic import BaseModel
import tempfile, os
import time
import logging

from ..services.asr import ASREngine
from ..services.chunker import split_sentences, make_chunks
from ..db import get_session
from ..models import SessionModel, TranscriptModel, ChunkModel
from ..config import settings
from ..delivery.client import deliver_chunk, deliver_final

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1")


class BatchOut(BaseModel):
    session_id: str
    text_full: str
    chunks: list[dict]


@router.post("/transcribe", response_model=BatchOut)
async def transcribe(
    file: UploadFile = File(...),
    session_id: str = Query(default_factory=lambda: os.urandom(6).hex()),
    lang: str = Query(default="ru-RU"),
):
    size = 0
    with tempfile.NamedTemporaryFile(
        suffix=os.path.splitext(file.filename or "")[-1] or ".webm", delete=False
    ) as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            size += len(chunk)
        path = f.name

    limit_mb = settings.limits[settings.app.tier].max_file_mb
    if size > limit_mb * 1024 * 1024:
        os.remove(path)
        raise HTTPException(413, f"file too large for tier {settings.app.tier}")

    # Start ASR processing with timing
    asr_start_time = time.time()
    asr = ASREngine()
    res = asr.transcribe_file(path)
    asr_duration_ms = int((time.time() - asr_start_time) * 1000)
    os.remove(path)

    # Log ASR processing details
    logger.info(f"ASR processing completed", extra={
        "event": "asr_completed",
        "session_id": session_id,
        "chunk_id": "media_file",
        "asr_duration_ms": asr_duration_ms,
        "file_size_bytes": size,
        "language": lang,
        "text_length": len(res.text) if res.text else 0,
        "service": "mod1_v2"
    })

    text = res.text.strip()
    sents = split_sentences(text)
    chunks = make_chunks(session_id, sents, start_seq=1)  # список DTO

    # 1) Сохраняем сессию, финал и чанки в локальную БД
    with get_session() as s:
        sess = s.get(SessionModel, session_id)
        if not sess:
            sess = SessionModel(id=session_id, lang=lang, tier=settings.app.tier)
            s.add(sess)

        tr = TranscriptModel(
            session_id=session_id,
            text_full=text,
            duration_sec=0.0,
            total_chunks=len(chunks),
            lang=lang,
        )
        s.add(tr)

        for ch in chunks:
            row = ChunkModel(
                session_id=session_id,
                chunk_id=ch.chunk_id,
                seq=ch.seq,
                text=ch.text,
                overlap_prefix=ch.overlap_prefix,
                lang=lang,                 # фикс: используем lang из запроса
                policy_json=str(ch.policy),
                hash=ch.hash,
            )
            s.add(row)

        s.commit()

    # 2) После успешного коммита: доставляем чанки в Модуль 2 (идемпотентность и подпись — внутри клиента)
    logger.info(f"Starting chunk delivery to Mod2", extra={
        "event": "delivery_started",
        "session_id": session_id,
        "total_chunks": len(chunks),
        "service": "mod1_v2"
    })
    
    for ch in chunks:
        payload = {
            "session_id": session_id,
            "chunk_id": ch.chunk_id,
            "seq": ch.seq,
            "text": ch.text,
            "overlap_prefix": ch.overlap_prefix,  # строка допустима по схеме
            "lang": lang,                          # строго вида ru-RU для валидации
        } 
        # HMAC-SHA256 + Idempotency-Key формируются в client.py
        await deliver_chunk(payload)
        
        logger.debug(f"Chunk delivered", extra={
            "event": "chunk_delivered", 
            "session_id": session_id,
            "chunk_id": ch.chunk_id,
            "seq": ch.seq,
            "service": "mod1_v2"
        })

    # 3) Доставляем финал
    final_payload = {
        "session_id": session_id,
        "text_full": text,
        "lang": lang,
        "duration_sec": 0.0,           # если появится реальная длительность — подставь сюда
        "total_chunks": len(chunks),
    }
    
    logger.info(f"Delivering final result to Mod2", extra={
        "event": "final_delivery",
        "session_id": session_id,
        "total_chunks": len(chunks),
        "final_text_length": len(text),
        "duration_sec": 0.0,
        "service": "mod1_v2"
    })
    
    await deliver_final(final_payload)

    # 4) Возвращаем результат batch-вызова как и раньше
    return BatchOut(
        session_id=session_id,
        text_full=text,
        chunks=[
            {
                "session_id": c.session_id,
                "chunk_id": c.chunk_id,
                "seq": c.seq,
                "text": c.text,
                "overlap_prefix": c.overlap_prefix,
                "lang": lang,          # фикс: отдаём тот же lang
                "policy": c.policy,
                "hash": c.hash,
                "created_at": getattr(c, "created_at", None),  # на случай, если DTO без поля
            }
            for c in chunks
        ],
    )
