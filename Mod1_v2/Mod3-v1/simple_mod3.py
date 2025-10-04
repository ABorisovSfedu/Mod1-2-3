#!/usr/bin/env python3
"""Упрощенная версия Mod3-v1 для запуска"""

import os
os.environ['DATABASE_URL'] = 'sqlite:///./mod3.db'
os.environ['MOD3_HOST'] = '0.0.0.0'
os.environ['MOD3_PORT'] = '9001'

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI(
    title="Mod3-v1 Simple",
    version="1.0.0",
    description="Visual Elements Mapping Service"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def health_check():
    return {
        "status": "ok",
        "service": "Mod3-v1",
        "version": "1.0.0",
        "database_url": "sqlite:///./mod3.db",
        "feature_flags": {
            "require_props": True,
            "names_normalize": True,
            "dedup_by_component": True,
            "at_least_one_main": True,
            "fallback_sections": True,
            "max_matches": 6
        }
    }

@app.get("/")
def root():
    return {
        "message": "Mod3-v1 - Visual Elements Mapping Service",
        "version": "1.0.0",
        "docs": "/docs"
    }

class MappingRequest(BaseModel):
    session_id: str
    entities: List[str] = []
    keyphrases: List[str] = []
    template: Optional[str] = None

@app.post("/v1/map")
def map_entities_to_layout(request: MappingRequest):
    """Простое сопоставление entities с компонентами"""
    
    # Базовое сопоставление
    mapping_rules = {
        "заголовок": "ui.heading",
        "кнопка": "ui.button", 
        "форма": "ui.form",
        "герои": "ui.hero",
        "подвал": "ui.footer",
        "футер": "ui.footer",
        "текст": "ui.text"
    }
    
    # Ищем совпадения
    components = []
    explanations = []
    
    for entity in request.entities + request.keyphrases:
        entity_lower = entity.lower()
        for term, component in mapping_rules.items():
            if term in entity_lower:
                components.append({
                    "component": component,
                    "props": {"text": entity.title()},
                    "confidence": 0.9,
                    "match_type": "fuzzy",
                    "term": entity
                })
                explanations.append({
                    "term": entity,
                    "matched_component": component,
                    "match_type": "fuzzy",
                    "score": 0.9
                })
                break
    
    # Fallback если нет совпадений
    if not components:
        components = [{
            "component": "ui.hero",
            "props": {"title": "Hello", "subtitle": "Welcome"},
            "confidence": 0.5,
            "match_type": "fallback",
            "term": "fallback"
        }]
        explanations.append({
            "term": "fallback",
            "matched_component": "ui.hero",
            "match_type": "fallback", 
            "score": 0.5
        })
    
    # Распределяем по секциям
    hero = [c for c in components if "ui.hero" == c["component"]]
    footer = [c for c in components if "ui.footer" == c["component"]]
    main = [c for c in components if c["component"] not in ["ui.hero", "ui.footer"]]
    
    # Если main пустая, добавляем контейнер
    if not main:
        main = [{
            "component": "ui.container",
            "props": {"maxWidth": "xl"},
            "confidence": 0.8,
            "match_type": "default",
            "term": "container"
        }]
    
    layout = {
        "template": request.template or "hero-main-footer",
        "sections": {
            "hero": hero,
            "main": main,
            "footer": footer
        },
        "count": len(components)
    }
    
    return {
        "status": "ok",
        "session_id": request.session_id,
        "layout": layout,
        "matches": components,
        "explanations": explanations
    }

@app.get("/v1/components")
def get_components():
    """Возвращает каталог компонентов"""
    
    components = [
        {
            "name": "ui.hero",
            "category": "branding",
            "example_props": {
                "title": "Добро пожаловать",
                "subtitle": "Демо приложение",
                "ctas": [
                    {"text": "Начать", "variant": "primary"}
                ]
            }
        },
        {
            "name": "ui.heading",
            "category": "content",
            "example_props": {
                "text": "Заголовок страницы",
                "level": 1
            }
        },
        {
            "name": "ui.button",
            "category": "action",
            "example_props": {
                "text": "Отправить",
                "variant": "primary"
            }
        },
        {
            "name": "ui.form",
            "category": "form", 
            "example_props": {
                "fields": [
                    {
                        "name": "email",
                        "label": "Email",
                        "type": "email",
                        "required": True
                    }
                ],
                "submitText": "Отправить"
            }
        },
        {
            "name": "ui.footer",
            "category": "meta",
            "example_props": {
                "links": ["О нас", "Контакты"]
            }
        }
    ]
    
    return {
        "status": "ok",
        "components": components
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Mod3-v1 Simple запущен на порту 9001")
    uvicorn.run(app, host="0.0.0.0", port=9001, log_level="info")
