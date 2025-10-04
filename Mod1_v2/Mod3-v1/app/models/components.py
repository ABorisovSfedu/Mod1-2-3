from sqlalchemy import Column, String, Text, Boolean, JSON, Integer
from .base import Base, TimestampMixin


class Component(Base, TimestampMixin):
    __tablename__ = "components"
    
    name = Column(String(255), nullable=False, unique=True, index=True)
    component_type = Column(String(100), nullable=False)  # ui.button, ui.form, ContactForm, etc.
    description = Column(Text)
    properties = Column(JSON)  # Дополнительные свойства компонента
    props_schema = Column(JSON)  # JSON schema для props
    example_props = Column(JSON)  # Пример props для компонента
    category = Column(String(50))  # action, form, list, card, table, chart, branding, splash, meta, contact, links
    min_span = Column(Integer, default=1)  # Минимальный span
    max_span = Column(Integer, default=12)  # Максимальный span
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Component(id={self.id}, name='{self.name}', type='{self.component_type}')>"

