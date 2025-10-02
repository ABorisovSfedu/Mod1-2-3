"""
Enhanced Layout Service for Mod3-v1 with feature flags
Provides robust layout generation with validation and fallbacks
"""
from typing import List, Dict, Any, Optional, Set
from sqlalchemy.orm import Session
from app.models import Template, Layout, Component
from app.schemas.validation import validate_layout_structure, ensure_default_component_values
import os
import logging
import json

logger = logging.getLogger(__name__)

class EnhancedLayoutService:
    def __init__(self, db: Session):
        self.db = db
        self._feature_flags = self._load_feature_flags()
    
    def _load_feature_flags(self) -> Dict[str, bool]:
        """Load feature flags from environment variables"""
        return {
            "require_props": os.getenv("M3_REQUIRE_PROPS", "true").lower() == "true",
            "names_normalize": os.getenv("M3_NAMES_NORMALIZE", "true").lower() == "true", 
            "dedup_by_component": os.getenv("M3_DEDUP_BY_COMPONENT", "true").lower() == "true",
            "at_least_one_main": os.getenv("M3_AT_LEAST_ONE_MAIN", "true").lower() == "true",
            "fallback_sections": os.getenv("M3_FALLBACK_SECTIONS", "true").lower() == "true",
        }
    
    def build_enhanced_layout(
        self, 
        session_id: str, 
        matches: List[Dict[str, Any]], 
        template_name: str = None
    ) -> Dict[str, Any]:
        """
        Builds enhanced layout with feature flags and validation
        """
        template = self._get_template(template_name)
        
        # Normalize component names if enabled
        if self._feature_flags["names_normalize"]:
            matches = self._normalize_component_names(matches)
        
        # Ensure components have props if enabled
        if self._feature_flags["require_props"]:
            matches = self._ensure_component_props(matches)
        
        # Group components by sections using enhanced categorization
        sections = self._group_components_by_enhanced_sections(matches, template)
        
        # Remove duplicates if enabled
        if self._feature_flags["dedup_by_component"]:
            sections = self._deduplicate_sections(sections)
        
        # Ensure main section is not empty if enabled
        if self._feature_flags["at_least_one_main"]:
            sections = self._ensure_main_section(sections)
        
        # Apply fallback sections if completely empty
        if self._feature_flags["fallback_sections"] and self._is_layout_empty(sections):
            logger.warning("Layout is empty, applying fallback sections", extra={
                "event": "fallback_layout_applied",
                "session_id": session_id,
                "service": "mod3_v1"
            })
            sections = self._create_fallback_sections()
        
        # Create final layout
        layout_data = {
            "template": template.name,
            "sections": sections,
            "count": sum(len(components) for components in sections.values())
        }
        
        # Validate layout before saving
        validated_layout = self._validate_layout(layout_data)
        
        # Save to database
        self._save_layout(session_id, template.id, validated_layout)
        
        logger.info("Enhanced layout built successfully", extra={
            "event": "enhanced_layout_built",
            "session_id": session_id,
            "template": template.name,
            "total_components": layout_data["count"],
            "hero_count": len(sections.get("hero", [])),
            "main_count": len(sections.get("main", [])),
            "footer_count": len(sections.get("footer", [])),
            "service": "mod3_v1"
        })
        
        return validated_layout
    
    def _normalize_component_names(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize component names to ui.* format"""
        normalized = []
        for match in matches:
            component_name = match.get("component", "").strip()
            if component_name:
                # Convert to ui.* format
                normalized_name = component_name.lower()
                if not normalized_name.startswith("ui."):
                    normalized_name = f"ui.{normalized_name}"
                
                match["component"] = normalized_name
                logger.debug("Normalized component name", extra={
                    "event": "component_normalized",
                    "original": component_name,
                    "normalized": normalized_name,
                    "service": "mod3_v1"
                })
            normalized.append(match)
        
        return normalized
    
    def _ensure_component_props(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensure all components have props from database examples"""
        enhanced_matches = []
        for match in matches:
            component_name = match.get("component", "")
            
            # Get component from database
            component = self.db.query(Component).filter(
                Component.component_type == component_name,
                Component.is_active == True
            ).first()
            
            if component and component.example_props:
                try:
                    # Parse example props
                    example_props = json.loads(component.example_props) if isinstance(component.example_props, str) else component.example_props
                    
                    # Merge with existing props
                    existing_props = match.get("props", {})
                    merged_props = {**example_props, **existing_props}
                    match["props"] = merged_props
                    
                    logger.debug("Enhanced component with props", extra={
                        "event": "component_props_enhanced",
                        "component": component_name,
                        "service": "mod3_v1"
                    })
                except Exception as e:
                    logger.warning(f"Failed to parse example props for {component_name}: {str(e)}")
            
            enhanced_matches.append(match)
        
        return enhanced_matches
    
    def _group_components_by_enhanced_sections(self, matches: List[Dict[str, Any]], template: Template) -> Dict[str, List[Dict[str, Any]]]:
        """Group components using enhanced categorization rules"""
        sections = {"hero": [], "main": [], "footer": []}
        
        # Enhanced categorization rules
        section_rules = {
            # Branding/Splash elements -> hero
            "ui.hero": "hero",
            "ui.welcome": "hero",
            "ui.navbar": "hero",
            "ui.breadcrumb": "hero",
            
            # Action/Content elements -> main  
            "ui.button": "main",
            "ui.heading": "main",
            "ui.text": "main",
            "ui.paragraph": "main",
            "ui.image": "main",
            "ui.form": "main",
            "ui.input": "main",
            "ui.textarea": "main",
            "ui.select": "main",
            "ui.checkbox": "main",
            "ui.radio": "main",
            "ui.switch": "main",
            "ui.card": "main",
            "ui.table": "main",
            "ui.chart": "main",
            "ui.list": "main",
            "ui.grid": "main",
            "ui.tabs": "main",
            "ui.accordion": "main",
            "ui.carousel": "main",
            "ui.modal": "main",
            "ui.tooltip": "main",
            "ui.popover": "main",
            
            # Meta/Navigation elements -> footer
            "ui.footer": "footer",
            "ui.sidebar": "footer",
            "ui.menu": "footer",
        }
        
        for match in matches:
            component_name = match.get("component", "").lower()
            section = section_rules.get(component_name, "main")  # default to main
            
            sections[section].append(match)
        
        return sections
    
    def _deduplicate_sections(self, sections: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Remove duplicate components within sections"""
        deduped = {}
        for section_name, components in sections.items():
            seen_components = set()
            unique_components = []
            
            for component in components:
                comp_name = component.get("component", "")
                if comp_name not in seen_components:
                    seen_components.add(comp_name)
                    unique_components.append(component)
            
            deduped[section_name] = unique_components
            
            if len(components) != len(unique_components):
                logger.debug(f"Deduplicated {len(components) - len(unique_components)} components in {section_name}")
        
        return deduped
    
    def _ensure_main_section(self, sections: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Ensure main section has at least one component"""
        main_count = len(sections.get("main", []))
        
        if main_count == 0:
            logger.info("Main section is empty, adding ui.container", extra={
                "event": "main_section_empty_fixed",
                "service": "mod3_v1"
            })
            
            container_component = {
                "component": "ui.container",
                "props": {
                    "padding": "lg",
                    "children": "Main content container"
                },
                "confidence": 0.9,
                "match_type": "fallback",
                "term": "content"
            }
            sections["main"] = [container_component]
        
        return sections
    
    def _is_layout_empty(self, sections: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Check if layout is completely empty"""
        total_components = sum(len(components) for components in sections.values())
        return total_components == 0
    
    def _create_fallback_sections(self) -> Dict[str, List[Dict[str, Any]]]:
        """Create minimal useful fallback layout"""
        return {
            "hero": [{
                "component": "ui.hero",
                "props": {
                    "title": "Добро пожаловать",
                    "subtitle": "Это демо сайт",
                    "ctas": [
                        {"text": "Начать", "variant": "primary"},
                        {"text": "Подробнее", "variant": "secondary"}
                    ]
                },
                "confidence": 0.9,
                "match_type": "fallback",
                "term": "hero"
            }],
            "main": [{
                "component": "ui.container", 
                "props": {
                    "padding": "lg",
                    "children": "Основной контент"
                },
                "confidence": 0.9,
                "match_type": "fallback",
                "term": "main"
            }],
            "footer": []
        }
    
    def _validate_layout(self, layout_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate layout structure and fix common issues"""
        try:
            # First apply default component values and basic fixes
            layout_data = self._apply_layout_defaults(layout_data)
            
            # Then run schema validation
            is_valid, errors = validate_layout_structure(layout_data)
            
            if not is_valid:
                logger.warning(f"Layout validation found {len(errors)} issues", extra={
                    "event": "layout_validation_issues",
                    "error_count": len(errors),
                    "errors": errors,
                    "service": "mod3_v1"
                })
                
                # Apply fallback sections if validation fails badly
                if len(errors) > 3:  # Too many errors, might be serious corruption
                    logger.warning("Too many validation errors, applying fallback", extra={
                        "event": "layout_validation_fallback",
                        "service": "mod3_v1"
                    })
                    layout_data = {
                        "template": "hero-main-footer",
                        "sections": self._create_fallback_sections(),
                        "count": 3
                    }
            
            return layout_data
            
        except Exception as e:
            logger.error(f"Layout validation failed: {str(e)}", extra={
                "event": "layout_validation_error",
                "error": str(e),
                "service": "mod3_v1"
            })
            # Return minimal valid layout
            return {
                "template": "hero-main-footer",
                "sections": self._create_fallback_sections(),
                "count": 3
            }
    
    def _apply_layout_defaults(self, layout_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values and basic fixes to layout"""
        # Ensure required fields
        if "template" not in layout_data:
            layout_data["template"] = "hero-main-footer"
        
        if "sections" not in layout_data:
            layout_data["sections"] = {"hero": [], "main": [], "footer": []}
        
        # Validate sections structure
        sections = layout_data["sections"]
        for section_name in ["hero", "main", "footer"]:
            if section_name not in sections:
                sections[section_name] = []
            
            # Ensure each component has required fields
            for component in sections[section_name]:
                # Apply component defaults
                enhanced_component = ensure_default_component_values(component)
                component.update(enhanced_component)
                
                # Fix common issues
                if not component.get("component"):
                    component["component"] = "ui.unknown"
                elif not component["component"].startswith("ui."):
                    component["component"] = f"ui.{component['component']}"
        
        # Ensure count is correct
        layout_data["count"] = sum(len(components) for components in sections.values())
        
        return layout_data
    
    def _get_template(self, template_name: str) -> Template:
        """Get template by name with fallback"""
        if not template_name:
            template_name = "hero-main-footer"
        
        template = self.db.query(Template).filter(
            Template.name == template_name,
            Template.is_active == True
        ).first()
        
        if not template:
            # Return default template
            template = self.db.query(Template).filter(
                Template.is_default == True,
                Template.is_active == True
            ).first()
        
        if not template:
            # Create basic template if none found
            template = Template(
                name="hero-main-footer",
                description="Basic hero-main-footer template",
                section_config=json.dumps({
                    "hero": {"title": "Hero Section", "required": False},
                    "main": {"title": "Main Content", "required": True},
                    "footer": {"title": "Footer", "required": False}
                }),
                is_default=True,
                is_active=True
            )
            self.db.add(template)
            self.db.commit()
        
        return template
    
    def _save_layout(self, session_id: str, template_id: int, layout_data: Dict[str, Any]) -> None:
        """Save layout to database"""
        try:
            layout = Layout(
                session_id=session_id,
                template_id=template_id,
                layout_data=json.dumps(layout_data),
                is_active=True
            )
            self.db.add(layout)
            self.db.commit()
            
            logger.info("Layout saved successfully", extra={
                "event": "layout_saved",
                "session_id": session_id,
                "template_id": template_id,
                "service": "mod3_v1"
            })
        except Exception as e:
            logger.error(f"Failed to save layout: {str(e)}", extra={
                "event": "layout_save_error",
                "session_id": session_id,
                "error": str(e),
                "service": "mod3_v1"
            })
            self.db.rollback()
            raise
