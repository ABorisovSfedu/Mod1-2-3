from typing import List, Optional
from pydantic import BaseModel, Field


# --- Ingest payloads ---

class IngestChunkRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    chunk_id: str = Field(..., min_length=1)
    seq: int = Field(..., ge=0, description="Порядковый номер чанка")
    text: str = Field(..., min_length=1)
    overlap_prefix: Optional[str] = Field(default=None)
    lang: str = Field(..., min_length=2, max_length=10)


class IngestFullRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    text_full: str = Field(..., min_length=1)
    lang: str = Field(..., min_length=2, max_length=10)


# --- Keyphrases & Mapping ---

class Keyphrase(BaseModel):
    text: str = Field(..., min_length=1, description="Исходная фраза (нижний регистр)")
    lemma: str = Field(..., min_length=1, description="Лемматизированная фраза, нижний регистр")
    confidence: float = Field(..., ge=0.0, le=1.0)


class MappingResult(BaseModel):
    keyphrase: Optional[Keyphrase] = None
    element: str
    score: float = Field(..., ge=0.0, le=1.0)


# --- Vocab schema ---

class VocabTerm(BaseModel):
    lemma: str = Field(..., min_length=1)
    aliases: List[str] = Field(default_factory=list)
    element: str = Field(..., min_length=1)


class VocabSchema(BaseModel):
    vocab_version: str = Field(..., min_length=1)
    terms: List[VocabTerm] = Field(default_factory=list)
