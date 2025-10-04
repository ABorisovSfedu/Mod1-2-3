from sqlalchemy import Column, String, Text, JSON, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Layout(Base, TimestampMixin):
    __tablename__ = "layouts"
    
    session_id = Column(String(255), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    layout_data = Column(JSON)  # Готовый layout в формате JSON
    components_count = Column(Integer, default=0)
    
    # Relationships
    template = relationship("Template", backref="layouts")
    
    def __repr__(self):
        return f"<Layout(id={self.id}, session_id='{self.session_id}')>"

