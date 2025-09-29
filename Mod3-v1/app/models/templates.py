from sqlalchemy import Column, String, Text, JSON, Boolean
from .base import Base, TimestampMixin


class Template(Base, TimestampMixin):
    __tablename__ = "templates"
    
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    structure = Column(JSON)  # Структура шаблона (секции и их порядок)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}')>"

