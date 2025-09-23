from sqlalchemy import select
from app.db import async_session
from app.models import IngestEvent
from sqlalchemy.exc import IntegrityError

async def save_chunk(data, idem_key):
    async with async_session() as s:
        ev = IngestEvent(
            idempotency_key=idem_key,
            session_id=data["session_id"],
            kind="chunk",
            payload=data,
            seq=data["seq"],
        )
        s.add(ev)
        try:
            await s.commit()
        except IntegrityError:
            await s.rollback()  # дубль — игнорим

async def save_final(data, idem_key):
    async with async_session() as s:
        ev = IngestEvent(
            idempotency_key=idem_key,
            session_id=data["session_id"],
            kind="final",
            payload=data,
            seq=None,
        )
        s.add(ev)
        try:
            await s.commit()
        except IntegrityError:
            await s.rollback()
