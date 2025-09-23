import time
from typing import Optional, Dict, Any
from app.services.tracing import log_event

async def process_chunk(data: Dict[str, Any], idem_key: Optional[str]):
    t0 = time.time()
    # TODO: сохранить в БД, обновить превью и т.п.
    log_event("chunk_ingested", session_id=data["session_id"], seq=data["seq"], latency_ms=int((time.time()-t0)*1000))

async def process_final(data: Dict[str, Any], idem_key: Optional[str]):
    t0 = time.time()
    # TODO: сохранить финал в БД, собрать layout и т.п.
    log_event("final_ingested", session_id=data["session_id"], seq=None, latency_ms=int((time.time()-t0)*1000))
