from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models import Template, Layout
from config.settings import settings


class LayoutService:
    def __init__(self, db: Session):
        self.db = db
    
    def build_layout(self, session_id: str, matches: List[Dict[str, Any]], template_name: str = None) -> Dict[str, Any]:
        """
        Строит layout на основе найденных сопоставлений
        """
        # Получаем шаблон
        template = self._get_template(template_name or settings.default_template)
        
        # Группируем компоненты по секциям
        sections = self._group_components_by_sections(matches, template)
        
        # Создаем layout
        layout_data = {
            "template": template.name,
            "sections": sections,
            "count": sum(len(components) for components in sections.values())
        }
        
        # Сохраняем в базу данных
        self._save_layout(session_id, template.id, layout_data)
        
        return layout_data
    
    def _get_template(self, template_name: str) -> Template:
        """Получает шаблон по имени"""
        template = self.db.query(Template).filter(
            Template.name == template_name,
            Template.is_active == True
        ).first()
        
        if not template:
            # Возвращаем шаблон по умолчанию
            template = self.db.query(Template).filter(
                Template.is_default == True,
                Template.is_active == True
            ).first()
        
        if not template:
            # Создаем базовый шаблон если не найден
            template = self._create_default_template()
        
        return template
    
    def _create_default_template(self) -> Template:
        """Создает шаблон по умолчанию"""
        template = Template(
            name="hero-main-footer",
            description="Default template with hero, main and footer sections",
            structure={
                "sections": ["hero", "main", "footer"],
                "rules": {
                    "ContactForm": "footer",
                    "ServicesGrid": "main",
                    "Hero": "hero"
                }
            },
            is_default=True
        )
        self.db.add(template)
        self.db.commit()
        return template
    
    def _group_components_by_sections(self, matches: List[Dict[str, Any]], template: Template) -> Dict[str, List[Dict[str, Any]]]:
        """Группирует компоненты по секциям согласно правилам шаблона"""
        sections = {section: [] for section in template.structure.get("sections", ["hero", "main", "footer"])}
        rules = template.structure.get("rules", {})
        
        for match in matches:
            component_type = match['component_type']
            section = rules.get(component_type, "main")  # По умолчанию в main
            
            if section in sections:
                sections[section].append({
                    "component": component_type,
                    "confidence": match['confidence'],
                    "match_type": match['match_type']
                })
        
        # Добавляем Hero компонент в hero секцию только если есть другие компоненты
        if "hero" in sections and not any(comp["component"] == "Hero" for comp in sections["hero"]):
            # Добавляем Hero только если есть хотя бы один компонент в других секциях
            has_components = any(len(sections[sec]) > 0 for sec in sections if sec != "hero")
            if has_components:
                sections["hero"].append({"component": "Hero", "confidence": 1.0, "match_type": "default"})
        
        return sections
    
    def _save_layout(self, session_id: str, template_id: int, layout_data: Dict[str, Any]):
        """Сохраняет layout в базу данных"""
        layout = Layout(
            session_id=session_id,
            template_id=template_id,
            layout_data=layout_data,
            components_count=layout_data["count"]
        )
        self.db.add(layout)
        self.db.commit()
    
    def get_layout(self, session_id: str) -> Dict[str, Any]:
        """Получает сохраненный layout по session_id"""
        layout = self.db.query(Layout).filter(Layout.session_id == session_id).first()
        if layout:
            return layout.layout_data
        return None
