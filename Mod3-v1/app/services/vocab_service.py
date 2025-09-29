from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models import Term, Synonym, Component, Mapping


class VocabService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_vocab(self) -> Dict[str, Any]:
        """Получает весь словарь терминов с компонентами"""
        terms = self.db.query(Term).filter(Term.is_active == True).all()
        
        vocab_terms = []
        for term in terms:
            # Получаем синонимы
            synonyms = [syn.synonym for syn in term.synonyms]
            
            # Получаем компоненты
            components = []
            for mapping in term.mappings:
                if mapping.is_active:
                    components.append({
                        "component": mapping.component.name,
                        "component_type": mapping.component.component_type,
                        "confidence": mapping.confidence
                    })
            
            vocab_terms.append({
                "term": term.term,
                "description": term.description,
                "synonyms": synonyms,
                "components": components
            })
        
        return {
            "vocab_version": "1.0.0",
            "terms_count": len(vocab_terms),
            "terms": vocab_terms
        }
    
    def sync_vocab(self, vocab_data: Dict[str, Any]) -> Dict[str, Any]:
        """Синхронизирует словарь с переданными данными"""
        try:
            terms_data = vocab_data.get("terms", [])
            
            for term_data in terms_data:
                self._sync_term(term_data)
            
            self.db.commit()
            
            return {
                "status": "success",
                "message": f"Синхронизировано {len(terms_data)} терминов",
                "synced_count": len(terms_data)
            }
        
        except Exception as e:
            self.db.rollback()
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _sync_term(self, term_data: Dict[str, Any]):
        """Синхронизирует один термин"""
        term_name = term_data.get("term")
        if not term_name:
            return
        
        # Создаем или обновляем термин
        term = self.db.query(Term).filter(Term.term == term_name).first()
        if not term:
            term = Term(
                term=term_name,
                description=term_data.get("description", "")
            )
            self.db.add(term)
            self.db.flush()  # Получаем ID
        
        # Синхронизируем синонимы
        synonyms = term_data.get("synonyms", [])
        for synonym_name in synonyms:
            if not self.db.query(Synonym).filter(
                Synonym.term_id == term.id,
                Synonym.synonym == synonym_name
            ).first():
                synonym = Synonym(
                    term_id=term.id,
                    synonym=synonym_name
                )
                self.db.add(synonym)
        
        # Синхронизируем компоненты
        components = term_data.get("components", [])
        for comp_data in components:
            comp_name = comp_data.get("component")
            comp_type = comp_data.get("component_type")
            confidence = comp_data.get("confidence", 1.0)
            
            if comp_name and comp_type:
                # Создаем или находим компонент
                component = self.db.query(Component).filter(Component.name == comp_name).first()
                if not component:
                    component = Component(
                        name=comp_name,
                        component_type=comp_type,
                        description=comp_data.get("description", "")
                    )
                    self.db.add(component)
                    self.db.flush()
                
                # Создаем маппинг
                if not self.db.query(Mapping).filter(
                    Mapping.term_id == term.id,
                    Mapping.component_id == component.id
                ).first():
                    mapping = Mapping(
                        term_id=term.id,
                        component_id=component.id,
                        confidence=confidence
                    )
                    self.db.add(mapping)

