from sqlalchemy import select
from app.db import async_session
from app.models import IngestEvent
from sqlalchemy.exc import IntegrityError
from typing import List, Dict, Any

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

def get_session_results(session_id: str) -> List[Dict[str, Any]]:
    """
    Синхронная функция для получения результатов сессии.
    Возвращает список записей с полями seq и mappings.
    """
    import asyncio
    from app.services.mapping import process_text_mapping
    
    async def _get_results():
        async with async_session() as s:
            # Получаем все события для сессии
            result = await s.execute(select(IngestEvent).where(IngestEvent.session_id == session_id))
            events = result.scalars().all()
            
            results = []
            for event in events:
                if event.kind == "chunk":
                    text = event.payload.get("text", "")
                    mappings = process_text_mapping(text)
                    if mappings:
                        results.append({
                            "seq": event.seq,
                            "mappings": [
                                {"element": m.element, "confidence": m.score} 
                                for m in mappings
                            ]
                        })
                elif event.kind == "final":
                    text = event.payload.get("text_full", "")
                    mappings = process_text_mapping(text)
                    if mappings:
                        results.append({
                            "seq": None,
                            "mappings": [
                                {"element": m.element, "confidence": m.score} 
                                for m in mappings
                            ]
                        })
            
            return results
    
    try:
        return asyncio.run(_get_results())
    except Exception as e:
        print(f"Error getting session results for {session_id}: {e}")
        return []
