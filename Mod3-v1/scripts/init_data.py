#!/usr/bin/env python3
"""
Скрипт для инициализации базовых данных в Mod3-v1
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Term, Synonym, Component, Mapping, Template
from config.settings import settings


def init_database():
    """Создает таблицы в базе данных"""
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы")


def init_basic_data():
    """Инициализирует базовые данные"""
    db = SessionLocal()
    
    try:
        # Создаем шаблон по умолчанию
        template = db.query(Template).filter(Template.name == "hero-main-footer").first()
        if not template:
            template = Template(
                name="hero-main-footer",
                description="Default template with hero, main and footer sections",
                structure={
                    "sections": ["hero", "main", "footer"],
                    "rules": {
                        "ContactForm": "footer",
                        "ServicesGrid": "main",
                        "Hero": "hero",
                        "ui.button": "main",
                        "ui.form": "main"
                    }
                },
                is_default=True
            )
            db.add(template)
            db.flush()
            print("✅ Шаблон создан")
        
        # Создаем базовые компоненты
        components_data = [
            {"name": "Hero", "component_type": "Hero", "description": "Главный баннер"},
            {"name": "ContactForm", "component_type": "ContactForm", "description": "Форма обратной связи"},
            {"name": "ServicesGrid", "component_type": "ServicesGrid", "description": "Сетка услуг"},
            {"name": "ui.button", "component_type": "ui.button", "description": "Кнопка"},
            {"name": "ui.form", "component_type": "ui.form", "description": "Форма"},
        ]
        
        for comp_data in components_data:
            component = db.query(Component).filter(Component.name == comp_data["name"]).first()
            if not component:
                component = Component(**comp_data)
                db.add(component)
        
        db.flush()
        print("✅ Компоненты созданы")
        
        # Создаем базовые термины и маппинги
        terms_data = [
            {
                "term": "кнопка",
                "description": "Элемент интерфейса для выполнения действий",
                "synonyms": ["button", "кнопочка"],
                "components": [{"name": "ui.button", "confidence": 1.0}]
            },
            {
                "term": "форма",
                "description": "Элемент для ввода данных",
                "synonyms": ["form", "формочка"],
                "components": [{"name": "ui.form", "confidence": 1.0}]
            },
            {
                "term": "обратная связь",
                "description": "Форма для связи с пользователями",
                "synonyms": ["contact", "связь", "контакт", "feedback"],
                "components": [{"name": "ContactForm", "confidence": 1.0}]
            },
            {
                "term": "услуги",
                "description": "Каталог предоставляемых услуг",
                "synonyms": ["services", "каталог", "сервисы"],
                "components": [{"name": "ServicesGrid", "confidence": 1.0}]
            }
        ]
        
        for term_data in terms_data:
            # Создаем термин
            term = db.query(Term).filter(Term.term == term_data["term"]).first()
            if not term:
                term = Term(
                    term=term_data["term"],
                    description=term_data["description"]
                )
                db.add(term)
                db.flush()
            
            # Создаем синонимы
            for synonym_name in term_data["synonyms"]:
                if not db.query(Synonym).filter(
                    Synonym.term_id == term.id,
                    Synonym.synonym == synonym_name
                ).first():
                    synonym = Synonym(
                        term_id=term.id,
                        synonym=synonym_name
                    )
                    db.add(synonym)
            
            # Создаем маппинги
            for comp_data in term_data["components"]:
                component = db.query(Component).filter(Component.name == comp_data["name"]).first()
                if component and not db.query(Mapping).filter(
                    Mapping.term_id == term.id,
                    Mapping.component_id == component.id
                ).first():
                    mapping = Mapping(
                        term_id=term.id,
                        component_id=component.id,
                        confidence=comp_data["confidence"]
                    )
                    db.add(mapping)
        
        db.commit()
        print("✅ Термины и маппинги созданы")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при инициализации данных: {e}")
        raise
    finally:
        db.close()


def main():
    """Основная функция"""
    print("🚀 Инициализация Mod3-v1...")
    
    try:
        init_database()
        init_basic_data()
        print("✅ Инициализация завершена успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

