from sqlalchemy import Column, String, Integer, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Mapping(Base, TimestampMixin):
    __tablename__ = "mappings"
    
    term_id = Column(Integer, ForeignKey("terms.id"), nullable=False)
    component_id = Column(Integer, ForeignKey("components.id"), nullable=False)
    confidence = Column(Float, default=1.0)  # Уверенность в сопоставлении
    is_active = Column(Boolean, default=True)
    
    # Relationships
    term = relationship("Term", backref="mappings")
    component = relationship("Component", backref="mappings")
    
    def __repr__(self):
        return f"<Mapping(id={self.id}, term_id={self.term_id}, component_id={self.component_id})>"
