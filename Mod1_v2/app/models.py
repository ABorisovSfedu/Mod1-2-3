from __future__ import annotations
import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field

class SessionModel(SQLModel, table=True):
    __tablename__ = "sessions"
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    lang: str = Field(default="ru-RU")
    tier: str = Field(default="Basic")
    started_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    ended_at: datetime | None = None
    status: str = Field(default="active")
    received_bytes: int = 0

class TranscriptModel(SQLModel, table=True):
    __tablename__ = "transcripts"
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(foreign_key="sessions.id", index=True)
    text_full: str = Field(default="")
    duration_sec: float = 0.0
    total_chunks: int = 0
    lang: str = Field(default="ru-RU")
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())

class ChunkModel(SQLModel, table=True):
    __tablename__ = "chunks"
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(foreign_key="sessions.id", index=True)
    chunk_id: str = Field(index=True)
    seq: int
    text: str
    overlap_prefix: str = ""
    lang: str = "ru-RU"
    policy_json: str = ""
    hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    delivered_at: datetime | None = None

class WebhookModel(SQLModel, table=True):
    __tablename__ = "webhooks"
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    url: str
    secret: str
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())