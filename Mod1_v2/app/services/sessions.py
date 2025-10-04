from __future__ import annotations
import asyncio, time, os
from dataclasses import dataclass, field
from typing import Dict
from datetime import datetime
from sqlmodel import select

from ..config import settings
from ..db import get_session
from ..models import SessionModel, TranscriptModel, ChunkModel
from .asr import ASREngine
from .chunker import split_sentences, make_chunks
from .webhooks import get_active_webhook, send_chunk

@dataclass
class LiveState:
    session_id: str
    tmp_path: str
    last_debounce: float = 0.0
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    emitted_seq: int = 0
    emitted_sentences: int = 0
    full_text: str = ""
    closed: bool = False

class SessionManager:
    def __init__(self) -> None:
        self.states: Dict[str, LiveState] = {}
        self.asr = ASREngine()

    def _ensure_session(self, session_id: str, lang: str, tier: str = "Basic") -> LiveState:
        if session_id in self.states:
            return self.states[session_id]
        os.makedirs("/app/tmp", exist_ok=True)
        tmp_path = f"/app/tmp/{session_id}.webm"
        state = LiveState(session_id=session_id, tmp_path=tmp_path)
        self.states[session_id] = state
        with get_session() as s:
            existing = s.get(SessionModel, session_id)
            if not existing:
                s.add(SessionModel(id=session_id, lang=lang, tier=tier))
                s.commit()
        return state

    async def append_audio(self, session_id: str, lang: str, data: bytes) -> None:
        state = self._ensure_session(session_id, lang)
        async with state.lock:
            with open(state.tmp_path, "ab") as f:
                f.write(data)
            state.last_debounce = time.time()
            with get_session() as s:
                m = s.get(SessionModel, session_id)
                if m:
                    m.received_bytes += len(data)
                    s.add(m); s.commit()
        asyncio.create_task(self._debounced_process(session_id, lang))

    async def _debounced_process(self, session_id: str, lang: str) -> None:
        await asyncio.sleep(settings.app.ws_debounce_ms / 1000.0)
        state = self.states.get(session_id)
        if not state or state.closed:
            return
        if time.time() - state.last_debounce < (settings.app.ws_debounce_ms / 1000.0) - 0.05:
            return
        await self._process_now(session_id, lang)

    async def _process_now(self, session_id: str, lang: str) -> None:
        state = self.states[session_id]
        async with state.lock:
            res = self.asr.transcribe_file(state.tmp_path)
            text = res.text.strip()
            if not text:
                return
            sents = split_sentences(text)
            new_sents = sents[state.emitted_sentences:]
            if not new_sents:
                return
            chunks = make_chunks(session_id, new_sents, start_seq=state.emitted_seq + 1)
            if not chunks:
                return
            webhook = await get_active_webhook()
            for ch in chunks:
                import orjson
                with get_session() as ds:
                    cm = ChunkModel(
                        session_id=session_id,
                        chunk_id=ch.chunk_id,
                        seq=ch.seq,
                        text=ch.text,
                        overlap_prefix=ch.overlap_prefix,
                        lang=ch.lang,
                        policy_json=orjson.dumps(ch.policy).decode("utf-8"),
                        hash=ch.hash,
                    )
                    ds.add(cm); ds.commit()
                if webhook:
                    payload = {
                        "session_id": ch.session_id,
                        "chunk_id": ch.chunk_id,
                        "seq": ch.seq,
                        "text": ch.text,
                        "overlap_prefix": ch.overlap_prefix,
                        "lang": ch.lang,
                        "policy": ch.policy,
                        "hash": ch.hash,
                        "created_at": datetime.utcnow().isoformat() + "Z"
                    }
                    try:
                        await send_chunk(webhook, payload)
                        with get_session() as ds:
                            row = ds.exec(select(ChunkModel).where(ChunkModel.chunk_id == ch.chunk_id)).first()
                            if row:
                                row.delivered_at = datetime.utcnow(); ds.add(row); ds.commit()
                    except Exception:
                        pass
                state.emitted_seq = ch.seq
            state.emitted_sentences = len(sents)
            state.full_text = text

    async def close_session(self, session_id: str, lang: str) -> dict:
        state = self.states.get(session_id)
        if not state:
            return {"session_id": session_id, "text_full": "", "duration_sec": 0.0, "total_chunks": 0, "lang": lang}
        await self._process_now(session_id, lang)
        async with state.lock:
            state.closed = True
            full = state.full_text
            with get_session() as s:
                sm = s.get(SessionModel, session_id)
                if sm:
                    sm.ended_at = datetime.utcnow(); sm.status = "closed"
                    s.add(sm); s.commit()
            with get_session() as s:
                total_chunks = s.exec(select(ChunkModel).where(ChunkModel.session_id == session_id)).all()
                total_chunks = len(total_chunks)
                tr = TranscriptModel(session_id=session_id, text_full=full, duration_sec=0.0, total_chunks=total_chunks, lang=lang)
                s.add(tr); s.commit()
            return {"session_id": session_id, "text_full": full, "duration_sec": 0.0, "total_chunks": total_chunks, "lang": lang}

SESSION_MANAGER = SessionManager()