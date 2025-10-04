from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.nlp.extract import split_sentences, lemmatize_phrase, extract_np_candidates

router = APIRouter(prefix="/debug", tags=["debug"])


class DebugParseRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Русский текст для парсинга")
    lang: str | None = Field(default="ru", description="Игнорируется, текущая реализация для RU")


@router.post("/parse")
def debug_parse(req: DebugParseRequest):
    sents = split_sentences(req.text)
    lemmas = lemmatize_phrase(req.text)
    nps = extract_np_candidates(req.text)
    return {
        "status": "ok",
        "sentences": sents,
        "lemmas": lemmas,
        "np_candidates": nps,
    }
