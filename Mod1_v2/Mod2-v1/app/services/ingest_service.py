import time
from typing import Optional, Dict, Any
from app.services.tracing import log_event
from app.services.store import save_chunk, save_final
from app.services.mapping import process_text_mapping

async def process_chunk(data: Dict[str, Any], idem_key: Optional[str]):
    t0 = time.time()
    
    # Сохраняем чанк в БД
    await save_chunk(data, idem_key)
    
    # Обрабатываем текст и создаем маппинги
    text = data.get("text", "")
    session_id = data["session_id"]
    seq = data["seq"]
    
    # Создаем маппинги для текста
    mappings = process_text_mapping(text)
    
    # Сохраняем маппинги (пока в логах)
    log_event("chunk_processed", 
              session_id=session_id, 
              seq=seq, 
              text_length=len(text),
              mappings_count=len(mappings),
              latency_ms=int((time.time()-t0)*1000))
    
    log_event("chunk_ingested", session_id=data["session_id"], seq=data["seq"], latency_ms=int((time.time()-t0)*1000))

async def process_final(data: Dict[str, Any], idem_key: Optional[str]):
    t0 = time.time()
    
    # Сохраняем финальный результат в БД
    await save_final(data, idem_key)
    
    # Обрабатываем полный текст
    text = data.get("text_full", "")
    session_id = data["session_id"]
    
    # Создаем маппинги для полного текста
    mappings = process_text_mapping(text)
    
    log_event("final_processed", 
              session_id=session_id, 
              text_length=len(text),
              mappings_count=len(mappings),
              latency_ms=int((time.time()-t0)*1000))
    
    log_event("final_ingested", session_id=data["session_id"], seq=None, latency_ms=int((time.time()-t0)*1000))
