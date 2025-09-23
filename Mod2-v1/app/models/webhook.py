from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from .base import Base

class Webhook(Base):
    __tablename__ = "webhooks"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    url_chunk: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    url_final: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    secret: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
