from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Synonym(Base, TimestampMixin):
    __tablename__ = "synonyms"
    
    term_id = Column(Integer, ForeignKey("terms.id"), nullable=False)
    synonym = Column(String(255), nullable=False, index=True)
    
    # Relationships
    term = relationship("Term", backref="synonyms")
    
    def __repr__(self):
        return f"<Synonym(id={self.id}, synonym='{self.synonym}')>"

