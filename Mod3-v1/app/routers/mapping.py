from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.services import MappingService, LayoutService
from app.services.enhanced_layout_service import EnhancedLayoutService
from app.models import Component
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["mapping"])


class MappingRequest(BaseModel):
    session_id: str
    entities: List[str] = []
    keyphrases: List[str] = []
    template: Optional[str] = None


class MappingResponse(BaseModel):
    status: str
    session_id: str
    layout: Dict[str, Any]
    matches: List[Dict[str, Any]]
    explanations: List[Dict[str, Any]]


@router.post("/map", response_model=MappingResponse)
def map_entities_to_layout(
    request: MappingRequest,
    db: Session = Depends(get_db)
):
    """
    Сопоставляет сущности и ключевые фразы с визуальными элементами
    и возвращает готовый layout
    """
    try:
        max_matches = int(os.getenv("M3_MAX_MATCHES", "6"))
        
        logger.info("Mapping request received", extra={
            "event": "mapping_request", 
            "session_id": request.session_id,
            "entities_count": len(request.entities),
            "keyphrases_count": len(request.keyphrases),
            "template": request.template,
            "service": "mod3_v1"
        })
        
        # Инициализируем сервисы
        mapping_service = MappingService(db)
        enhanced_layout_service = EnhancedLayoutService(db)
        
        # Находим сопоставления с ограничением
        all_matches = mapping_service.find_matches(
            entities=request.entities,
            keyphrases=request.keyphrases
        )
        
        # Ограничиваем количество matches согласно ENV
        matches = all_matches[:max_matches]
        
        if len(all_matches) > max_matches:
            logger.info(f"Limited matches from {len(all_matches)} to {max_matches}", extra={
                "event": "matches_limited",
                "session_id": request.session_id,
                "original_count": len(all_matches),
                "limited_count": max_matches,
                "service": "mod3_v1"
            })
        
        # Строим улучшенный layout с фичефлагами
        layout = enhanced_layout_service.build_enhanced_layout(
            session_id=request.session_id,
            matches=matches,
            template_name=request.template
        )
        
        # Создаем explanations из matches
        explanations = []
        for match in matches:
            explanations.append({
                "term": match.get("term", ""),
                "matched_component": match.get("component", ""),
                "match_type": match.get("match_type", ""),
                "score": match.get("score", 0.0),
                "rule_id": match.get("rule_id")
            })
        
        logger.info("Mapping completed successfully", extra={
            "event": "mapping_completed",
            "session_id": request.session_id,
            "matches_found": len(matches),
            "layout_components": layout.get("count", 0),
            "service": "mod3_v1"
        })
        
        return MappingResponse(
            status="ok",
            session_id=request.session_id,
            layout=layout,
            matches=matches,
            explanations=explanations
        )
    
    except Exception as e:
        logger.error(f"Mapping error: {str(e)}", extra={
            "event": "mapping_error",
            "session_id": request.session_id if request else "unknown",
            "error": str(e),
            "service": "mod3_v1"
        })
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layout/{session_id}")
def get_layout(session_id: str, db: Session = Depends(get_db)):
    """Получает сохраненный layout по session_id"""
    layout_service = LayoutService(db)
    layout = layout_service.get_layout(session_id)
    
    if not layout:
        raise HTTPException(status_code=404, detail="Layout not found")
    
    return {
        "status": "ok",
        "session_id": session_id,
        "layout": layout
    }


@router.get("/components")
def get_components(db: Session = Depends(get_db)):
    """Получает список всех компонентов с их схемами и примерами props"""
    try:
        components = db.query(Component).filter(Component.is_active == True).all()
        
        result = []
        for component in components:
            result.append({
                "name": component.component_type,
                "props_schema": component.props_schema,
                "example_props": component.example_props,
                "category": component.category,
                "min_span": component.min_span,
                "max_span": component.max_span
            })
        
        return {
            "status": "ok",
            "components": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

