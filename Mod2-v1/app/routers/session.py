from fastapi import APIRouter
from app.services.layout import build_layout_for_session
from app.services.store import get_session_results
from app.services.nlp_normalization import extract_and_normalize_entities, deduplicate_list
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v2/session", tags=["session"])


@router.get("/{session_id}/layout")
def get_session_layout(session_id: str):
    layout = build_layout_for_session(session_id)
    return {"status": "ok", "session_id": session_id, "layout": layout}


@router.get("/{session_id}/entities")
def get_session_entities(session_id: str):
    """
    Возвращает нормализованные entities и keyphrases для сессии.
    Этот endpoint используется веб-приложением для получения данных
    и последующей передачи в Mod3.
    """
    try:
        results = get_session_results(session_id)
        
        # Собираем и нормализуем все entities и keyphrases из всех чанков
        all_entities = []
        all_keyphrases = []
        full_text_parts = []
        
        for result in results:
            # Собираем исходные данные
            all_entities.extend(result.get("entities", []))
            all_keyphrases.extend(result.get("keyphrases", []))
            
            # Собираем исходный текст для повторной экстракции
            mappings = result.get("mappings", [])
            for mapping in mappings:
                # Если есть элемент, определяющий контекст
                element = mapping.get("element")
                if element:
                    full_text_parts.append(element)
        
        # Нормализуем entities и keyphrases
        unique_entities = deduplicate_list(all_entities)
        unique_keyphrases = deduplicate_list(all_keyphrases)
        
        # Если NLP_DEBUG включен, проверим нормализацию исходного текста
        full_text = " ".join(full_text_parts)
        if full_text.strip():
            re_extracted_entities, re_extracted_keyphrases = extract_and_normalize_entities(full_text)
            if re_extracted_entities or re_extracted_keyphrases:
                logger.info("Re-extracted NLP entities", extra={
                    "event": "nlp_re_extraction",
                    "session_id": session_id,
                    "original_entities": len(unique_entities),
                    "original_keyphrases": len(unique_keyphrases),
                    "re_extracted_entities": len(re_extracted_entities),
                    "re_extracted_keyphrases": len(re_extracted_keyphrases),
                    "service": "mod2_v1"
                })
        
        logger.info("Entities endpoint called", extra={
            "event": "entities_endpoint",
            "session_id": session_id,
            "entities_count": len(unique_entities),
            "keyphrases_count": len(unique_keyphrases),
            "chunks_processed": len(results),
            "service": "mod2_v1"
        })
        
        return {
            "status": "ok",
            "session_id": session_id,
            "entities": unique_entities,
            "keyphrases": unique_keyphrases,
            "chunks_processed": len(results)
        }
        
    except Exception as e:
        logger.error(f"Entities endpoint error: {str(e)}", extra={
            "event": "entities_endpoint_error",
            "session_id": session_id,
            "error": str(e),
            "service": "mod2_v1"
        })
        raise
