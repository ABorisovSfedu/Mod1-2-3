from sqlalchemy import Column, String, Text, Boolean, JSON
from .base import Base, TimestampMixin


class Component(Base, TimestampMixin):
    __tablename__ = "components"
    
    name = Column(String(255), nullable=False, unique=True, index=True)
    component_type = Column(String(100), nullable=False)  # ui.button, ui.form, ContactForm, etc.
    description = Column(Text)
    properties = Column(JSON)  # Дополнительные свойства компонента
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Component(id={self.id}, name='{self.name}', type='{self.component_type}')>"

