from sqlalchemy import String, JSON, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from .base import Base  # <— ВАЖНО

class IngestEvent(Base):
    __tablename__ = "ingest_events"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    session_id: Mapped[str] = mapped_column(String(128), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    seq: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_ingest_idem"),
    )
