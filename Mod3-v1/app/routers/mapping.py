from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.services import MappingService, LayoutService

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
        # Инициализируем сервисы
        mapping_service = MappingService(db)
        layout_service = LayoutService(db)
        
        # Находим сопоставления
        matches = mapping_service.find_matches(
            entities=request.entities,
            keyphrases=request.keyphrases
        )
        
        # Строим layout
        layout = layout_service.build_layout(
            session_id=request.session_id,
            matches=matches,
            template_name=request.template
        )
        
        return MappingResponse(
            status="ok",
            session_id=request.session_id,
            layout=layout,
            matches=matches
        )
    
    except Exception as e:
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

