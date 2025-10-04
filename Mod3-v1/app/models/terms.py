from sqlalchemy import Column, String, Text, Boolean
from .base import Base, TimestampMixin


class Term(Base, TimestampMixin):
    __tablename__ = "terms"
    
    term = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Term(id={self.id}, term='{self.term}')>"

