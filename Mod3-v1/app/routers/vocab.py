from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.services import VocabService

router = APIRouter(prefix="/v1", tags=["vocab"])


class VocabSyncRequest(BaseModel):
    vocab_version: str
    terms: list


@router.get("/vocab")
def get_vocab(db: Session = Depends(get_db)):
    """Получает весь словарь терминов с компонентами"""
    try:
        vocab_service = VocabService(db)
        return vocab_service.get_vocab()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vocab/sync")
def sync_vocab(request: VocabSyncRequest, db: Session = Depends(get_db)):
    """Синхронизирует словарь с переданными данными"""
    try:
        vocab_service = VocabService(db)
        result = vocab_service.sync_vocab(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

