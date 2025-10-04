from __future__ import annotations
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from ..db import get_session
from ..models import TranscriptModel, ChunkModel

router = APIRouter(prefix="/v1/session")

@router.get("/{sid}/text")
async def get_text(sid: str):
    with get_session() as s:
        tr = s.exec(select(TranscriptModel).where(TranscriptModel.session_id == sid)).first()
        if not tr:
            raise HTTPException(404, "not found")
        return {"session_id": sid, "text_full": tr.text_full, "lang": tr.lang}

@router.get("/{sid}/chunks")
async def get_chunks(sid: str):
    with get_session() as s:
        items = s.exec(select(ChunkModel).where(ChunkModel.session_id == sid).order_by(ChunkModel.seq.asc())).all()
        out = []
        for it in items:
            out.append({
                "session_id": it.session_id,
                "chunk_id": it.chunk_id,
                "seq": it.seq,
                "text": it.text,
                "overlap_prefix": it.overlap_prefix,
                "lang": it.lang,
                "policy": it.policy_json,
                "hash": it.hash,
                "created_at": it.created_at.isoformat() + "Z"
            })
        return out