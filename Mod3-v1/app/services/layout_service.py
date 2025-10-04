from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models import Template, Layout, Component
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
            # Применяем новые правила раскладки
            section = self._get_section_by_category(component_type, rules)
            
            if section in sections:
                # Нормализуем имя компонента
                normalized_component = self._normalize_component_name(component_type)
                
                # Получаем props для компонента
                props = self._get_component_props(normalized_component)
                
                sections[section].append({
                    "component": normalized_component,
                    "props": props,
                    "confidence": match['confidence'],
                    "match_type": match['match_type']
                })
        
        # Применяем feature flags
        if settings.dedup_by_component:
            sections = self._deduplicate_by_component(sections)
        
        if settings.fallback_sections:
            sections = self._add_fallback_sections(sections)
        
        if settings.at_least_one_main:
            sections = self._ensure_at_least_one_main(sections)
        
        return sections
    
    def _get_section_by_category(self, component_type: str, rules: Dict[str, str]) -> str:
        """Определяет секцию на основе категории компонента"""
        # Получаем компонент из БД для определения категории
        component = self.db.query(Component).filter(
            Component.component_type == component_type,
            Component.is_active == True
        ).first()
        
        if component and component.category:
            # Новые правила раскладки
            category_rules = {
                'action': 'main',
                'form': 'main', 
                'list': 'main',
                'card': 'main',
                'table': 'main',
                'chart': 'main',
                'branding': 'hero',
                'splash': 'hero',
                'meta': 'footer',
                'contact': 'footer',
                'links': 'footer'
            }
            return category_rules.get(component.category, rules.get(component_type, "main"))
        
        return rules.get(component_type, "main")
    
    def _normalize_component_name(self, component_name: str) -> str:
        """Нормализует имя компонента к формату ui.*"""
        if not settings.names_normalize:
            return component_name
            
        # Если уже в формате ui.*, возвращаем как есть
        if component_name.startswith('ui.'):
            return component_name
            
        # Конвертируем в snake_case и добавляем префикс ui.
        import re
        snake_case = re.sub('([A-Z]+)', r'_\1', component_name).lower().strip('_')
        return f"ui.{snake_case}"
    
    def _get_component_props(self, component_name: str) -> Dict[str, Any]:
        """Получает props для компонента"""
        if not settings.require_props:
            return {}
            
        component = self.db.query(Component).filter(
            Component.component_type == component_name,
            Component.is_active == True
        ).first()
        
        if component and component.example_props:
            return component.example_props
        
        # Возвращаем пустые props если не найдены
        return {}
    
    def _deduplicate_by_component(self, sections: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Удаляет дубликаты по имени компонента в секции"""
        for section_name, components in sections.items():
            seen_components = {}
            for component in components:
                comp_name = component['component']
                if comp_name not in seen_components or component['confidence'] > seen_components[comp_name]['confidence']:
                    seen_components[comp_name] = component
            sections[section_name] = list(seen_components.values())
        
        return sections
    
    def _add_fallback_sections(self, sections: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Добавляет fallback секции если они пустые"""
        # Проверяем, есть ли хотя бы один компонент в любой секции
        has_any_components = any(len(components) > 0 for components in sections.values())
        
        if not has_any_components:
            # Добавляем hero секцию
            if "hero" in sections:
                hero_props = self._get_component_props("ui.hero")
                sections["hero"] = [{"component": "ui.hero", "props": hero_props, "confidence": 1.0, "match_type": "fallback"}]
            
            # Добавляем main секцию
            if "main" in sections:
                container_props = self._get_component_props("ui.container")
                sections["main"] = [{"component": "ui.container", "props": container_props, "confidence": 1.0, "match_type": "fallback"}]
        
        return sections
    
    def _ensure_at_least_one_main(self, sections: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Обеспечивает наличие хотя бы одного блока в main секции"""
        if "main" in sections and len(sections["main"]) == 0:
            container_props = self._get_component_props("ui.container")
            sections["main"] = [{"component": "ui.container", "props": container_props, "confidence": 1.0, "match_type": "fallback"}]
        
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
