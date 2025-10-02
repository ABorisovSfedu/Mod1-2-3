#!/usr/bin/env python3
"""
Enhanced initialization script for Mod3-v1 
Adds comprehensive components with proper props examples
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Term, Synonym, Component, Mapping, Template
import json

def init_database():
    """Creates database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

def init_enhanced_components():
    """Initialize enhanced component catalog with proper example props"""
    db = SessionLocal()
    
    try:
        # Enhanced components with detailed props
        components_data = [
            {
                "component_type": "ui.hero",
                "category": "branding",
                "tags": ["hero", "welcome", "splash"],
                "props_schema": {
                    "title": {"type": "string", "required": True},
                    "subtitle": {"type": "string", "required": False},
                    "ctas": {"type": "array", "items": {"type": "object"}}
                },
                "example_props": {
                    "title": "Добро пожаловать",
                    "subtitle": "Это демо сайт",
                    "ctas": [
                        {"text": "Начать", "variant": "primary"},
                        {"text": "Подробнее", "variant": "secondary"}
                    ]
                },
                "min_span": 12,
                "max_span": 12
            },
            {
                "component_type": "ui.container",
                "category": "layout",
                "tags": ["container", "wrapper"],
                "props_schema": {
                    "padding": {"type": "string", "enum": ["sm", "md", "lg", "xl"]},
                    "children": {"type": "string"}
                },
                "example_props": {
                    "padding": "lg",
                    "children": "Основной контент"
                },
                "min_span": 1,
                "max_span": 12
            },
            {
                "component_type": "ui.heading",
                "category": "content",
                "tags": ["heading", "title"],
                "props_schema": {
                    "text": {"type": "string", "required": True},
                    "level": {"type": "integer", "minimum": 1, "maximum": 6},
                    "size": {"type": "string", "enum": ["sm", "md", "lg", "xl"]}
                },
                "example_props": {
                    "text": "Заголовок",
                    "level": 1,
                    "size": "xl"
                },
                "min_span": 6,
                "max_span": 12
            },
            {
                "component_type": "ui.text",
                "category": "content",
                "tags": ["text", "paragraph"],
                "props_schema": {
                    "text": {"type": "string", "required": True},
                    "alignment": {"type": "string", "enum": ["left", "center", "right"]}
                },
                "example_props": {
                    "text": "Описание блока текста",
                    "alignment": "left"
                },
                "min_span": 4,
                "max_span": 12
            },
            {
                "component_type": "ui.button",
                "category": "action",
                "tags": ["button", "action"],
                "props_schema": {
                    "text": {"type": "string", "required": True},
                    "variant": {"type": "string", "enum": ["primary", "secondary", "outline"]},
                    "size": {"type": "string", "enum": ["sm", "md", "lg"]}
                },
                "example_props": {
                    "text": "Отправить",
                    "variant": "primary",
                    "size": "md"
                },
                "min_span": 2,
                "max_span": 4
            },
            {
                "component_type": "ui.form",
                "category": "form",
                "tags": ["form", "input"],
                "props_schema": {
                    "fields": {"type": "array", "items": {"type": "object"}},
                    "submitText": {"type": "string"}
                },
                "example_props": {
                    "fields": [
                        {"name": "email", "label": "Email", "type": "email", "required": True},
                        {"name": "message", "label": "Сообщение", "type": "textarea"}
                    ],
                    "submitText": "Отправить"
                },
                "min_span": 6,
                "max_span": 12
            },
            {
                "component_type": "ui.card",
                "category": "content",
                "tags": ["card", "content"],
                "props_schema": {
                    "title": {"type": "string"},
                    "text": {"type": "string"},
                    "image": {"type": "string"}
                },
                "example_props": {
                    "title": "Карточка",
                    "text": "Краткое описание карточки",
                    "image": "/images/card.jpg"
                },
                "min_span": 3,
                "max_span": 6
            },
            {
                "component_type": "ui.footer",
                "category": "meta",
                "tags": ["footer", "links"],
                "props_schema": {
                    "columns": {"type": "array", "items": {"type": "object"}}
                },
                "example_props": {
                    "columns": [
                        {"title": "Компания", "links": ["О нас", "Контакты"]},
                        {"title": "Поддержка", "links": ["Помощь", "FAQ"]}
                    ]
                },
                "min_span": 12,
                "max_span": 12
            }
        ]
        
        # Create templates
        template = db.query(Template).filter(Template.name == "hero-main-footer").first()
        if not template:
            template = Template(
                name="hero-main-footer",
                description="Enhanced hero-main-footer template",
                section_config=json.dumps({
                    "hero": {"title": "Hero Section", "required": False, "max_components": 3},
                    "main": {"title": "Main Content", "required": True, "max_components": 10},
                    "footer": {"title": "Footer", "required": False, "max_components": 4}
                }),
                is_default=True,
                is_active=True
            )
            db.add(template)
            db.flush()
            print("✅ Enhanced template created")
        
        # Clear existing components and create new ones
        db.query(Component).delete()
        
        for comp_data in components_data:
            component = Component(
                component_type=comp_data["component_type"],
                category=comp_data["category"],
                description=f"Enhanced {comp_data['component_type']} component",
                props_schema=json.dumps(comp_data["props_schema"]),
                example_props=json.dumps(comp_data["example_props"]),
                min_span=comp_data["min_span"],
                max_span=comp_data["max_span"],
                tags=json.dumps(comp_data["tags"]),
                is_active=True
            )
            db.add(component)
        
        db.flush()
        print(f"✅ {len(components_data)} enhanced components created")
        
        # Create terms and mappings
        terms_data = [
            # Hero/Splash terms
            {"term": "герой", "synonyms": ["шапка", "баннер"], "component": "ui.hero"},
            {"term": "добро пожаловать", "synonyms": ["приветствие"], "component": "ui.hero"},
            {"term": "сайт", "synonyms": ["вест", "портал"], "component": "ui.hero"},
            
            # Content terms
            {"term": "заголовок", "synonyms": ["титул", "header"], "component": "ui.heading"},
            {"term": "текст", "synonyms": ["описание", "контент"], "component": "ui.text"},
            {"term": "параграф", "synonyms": ["абзац"], "component": "ui.text"},
            
            # Action terms
            {"term": "кнопка", "synonyms": ["баттон", "кнопочка"], "component": "ui.button"},
            {"term": "отправить", "synonyms": ["послать"], "component": "ui.button"},
            
            # Form terms
            {"term": "форма", "synonyms": ["анкета"], "component": "ui.form"},
            {"term": "поле ввода", "synonyms": ["инпут"], "component": "ui.form"},
            
            # Content structure terms
            {"term": "карточка", "synonyms": ["card"], "component": "ui.card"},
            {"term": "контейнер", "synonyms": ["обертка"], "component": "ui.container"},
            
            # Footer terms
            {"term": "подвал", "synonyms": ["футер", "footer"], "component": "ui.footer"},
            {"term": "ссылки", "synonyms": ["линки"], "component": "ui.footer"},
        ]
        
        # Clear existing mappings and create new ones
        db.query(Mapping).delete()
        db.query(Synonym).delete()
        db.query(Term).delete()
        
        for term_data in terms_data:
            # Create main term
            term = Term(
                term=term_data["term"],
                category="user_input",
                priority=1.0,
                is_active=True
            )
            db.add(term)
            db.flush()
            
            # Create synonyms
            for synonym_text in term_data["synonyms"]:
                synonym = Synonym(
                    synonym=synonym_text,
                    term_id=term.id,
                    is_active=True
                )
                db.add(synonym)
            
            # Create mapping
            mapping = Mapping(
                term_id=term.id,
                component_type=term_data["component"],
                match_type="exact",
                priority=1.0,
                is_active=True
            )
            db.add(mapping)
        
        db.commit()
        print(f"✅ {len(terms_data)} terms with mappings created")
        
        print("✅ Enhanced data initialization completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Initializing enhanced Mod3-v1 data...")
    init_database()
    init_enhanced_components()
    print("🎉 Enhanced initialization complete!")
