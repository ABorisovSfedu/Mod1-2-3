from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from rapidfuzz import fuzz
from app.models import Term, Synonym, Component, Mapping
from config.settings import settings
import re


class MappingService:
    def __init__(self, db: Session):
        self.db = db
        self.fuzzy_threshold = settings.fuzzy_threshold
        self.max_matches = settings.max_matches
    
    def find_matches(self, entities: List[str], keyphrases: List[str]) -> List[Dict[str, Any]]:
        """
        Находит сопоставления для переданных сущностей и ключевых фраз
        """
        matches = []
        
        # Объединяем все входные данные
        all_terms = entities + keyphrases
        
        for term in all_terms:
            term_lower = term.lower().strip()
            
            # 1. Точное совпадение
            exact_match = self._find_exact_match(term_lower)
            if exact_match:
                matches.append(exact_match)
                continue
            
            # 2. Поиск по синонимам
            synonym_match = self._find_synonym_match(term_lower)
            if synonym_match:
                matches.append(synonym_match)
                continue
            
            # 3. Fuzzy matching
            fuzzy_match = self._find_fuzzy_match(term_lower)
            if fuzzy_match:
                matches.append(fuzzy_match)
        
        # Удаляем дубликаты и сортируем по уверенности
        unique_matches = self._deduplicate_matches(matches)
        sorted_matches = sorted(unique_matches, key=lambda x: x['confidence'], reverse=True)
        
        # Ограничиваем количество совпадений
        return sorted_matches[:self.max_matches]
    
    def _find_exact_match(self, term: str) -> Optional[Dict[str, Any]]:
        """Поиск точного совпадения"""
        db_term = self.db.query(Term).filter(
            Term.term == term,
            Term.is_active == True
        ).first()
        
        if db_term:
            mapping = self.db.query(Mapping).filter(
                Mapping.term_id == db_term.id,
                Mapping.is_active == True
            ).first()
            
            if mapping:
                return {
                    'term': db_term.term,
                    'component': mapping.component.name,
                    'component_type': mapping.component.component_type,
                    'confidence': mapping.confidence,
                    'match_type': 'exact',
                    'rule_id': mapping.id,
                    'score': 1.0
                }
        
        return None
    
    def _find_synonym_match(self, term: str) -> Optional[Dict[str, Any]]:
        """Поиск по синонимам"""
        synonym = self.db.query(Synonym).filter(
            Synonym.synonym == term
        ).first()
        
        if synonym and synonym.term.is_active:
            mapping = self.db.query(Mapping).filter(
                Mapping.term_id == synonym.term_id,
                Mapping.is_active == True
            ).first()
            
            if mapping:
                return {
                    'term': synonym.term.term,
                    'component': mapping.component.name,
                    'component_type': mapping.component.component_type,
                    'confidence': mapping.confidence * 0.9,  # Немного снижаем уверенность для синонимов
                    'match_type': 'synonym',
                    'rule_id': mapping.id,
                    'score': 0.9
                }
        
        return None
    
    def _find_fuzzy_match(self, term: str) -> Optional[Dict[str, Any]]:
        """Fuzzy matching с использованием RapidFuzz"""
        best_match = None
        best_score = 0
        
        # Поиск по терминам
        terms = self.db.query(Term).filter(Term.is_active == True).all()
        for db_term in terms:
            score = fuzz.ratio(term, db_term.term.lower()) / 100.0
            if score > best_score and score >= self.fuzzy_threshold:
                mapping = self.db.query(Mapping).filter(
                    Mapping.term_id == db_term.id,
                    Mapping.is_active == True
                ).first()
                
                if mapping:
                    best_score = score
                    best_match = {
                        'term': db_term.term,
                        'component': mapping.component.name,
                        'component_type': mapping.component.component_type,
                        'confidence': mapping.confidence * score * 0.8,  # Снижаем уверенность для fuzzy
                        'match_type': 'fuzzy',
                        'rule_id': mapping.id,
                        'score': score
                    }
        
        # Поиск по синонимам
        synonyms = self.db.query(Synonym).all()
        for synonym in synonyms:
            if synonym.term.is_active:
                score = fuzz.ratio(term, synonym.synonym.lower()) / 100.0
                if score > best_score and score >= self.fuzzy_threshold:
                    mapping = self.db.query(Mapping).filter(
                        Mapping.term_id == synonym.term_id,
                        Mapping.is_active == True
                    ).first()
                    
                    if mapping:
                        best_score = score
                        best_match = {
                            'term': synonym.term.term,
                            'component': mapping.component.name,
                            'component_type': mapping.component.component_type,
                            'confidence': mapping.confidence * score * 0.7,  # Еще больше снижаем для синонимов
                            'match_type': 'fuzzy_synonym',
                            'rule_id': mapping.id,
                            'score': score
                        }
        
        return best_match
    
    def _deduplicate_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Удаляет дубликаты по компонентам, оставляя лучший match"""
        seen_components = {}
        
        for match in matches:
            component = match['component']
            if component not in seen_components or match['confidence'] > seen_components[component]['confidence']:
                seen_components[component] = match
        
        return list(seen_components.values())
    
    def normalize_component_name(self, component_name: str) -> str:
        """Нормализует имя компонента к формату ui.*"""
        if not settings.names_normalize:
            return component_name
            
        # Если уже в формате ui.*, возвращаем как есть
        if component_name.startswith('ui.'):
            return component_name
            
        # Конвертируем в snake_case и добавляем префикс ui.
        # Hero -> ui.hero, ContactForm -> ui.contact_form
        snake_case = re.sub('([A-Z]+)', r'_\1', component_name).lower().strip('_')
        return f"ui.{snake_case}"

