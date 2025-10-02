"""
JSON Schema validation for Mod3-v1 layouts
Provides robust validation before layout responses
"""
import json
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Layout validation schema
LAYOUT_SCHEMA = {
    "type": "object",
    "required": ["template", "sections"],
    "properties": {
        "template": {
            "type": "string",
            "enum": ["hero-main-footer", "simple-main", "full-width"]
        },
        "sections": {
            "type": "object",
            "required": ["hero", "main", "footer"],
            "properties": {
                "hero": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/component"},
                    "maxItems": 5
                },
                "main": {
                    "type": "array", 
                    "items": {"$ref": "#/definitions/component"},
                    "maxItems": 15,
                    "minItems": 0
                },
                "footer": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/component"},
                    "maxItems": 10
                }
            },
            "additionalProperties": False
        },
        "count": {
            "type": "integer",
            "minimum": 0
        }
    },
    "definitions": {
        "component": {
            "type": "object",
            "required": ["component"],
            "properties": {
                "component": {
                    "type": "string",
                    "pattern": "^ui\\.[a-z_]+$",
                    "description": "Component type in ui.* format"
                },
                "props": {
                    "type": "object",
                    "description": "Component properties"
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.5
                },
                "match_type": {
                    "type": "string",
                    "enum": ["exact", "synonym", "fuzzy", "fallback"],
                    "default": "fallback"
                },
                "term": {
                    "type": "string",
                    "description": "Original term that matched this component"
                }
            },
            "additionalProperties": True
        }
    },
    "additionalProperties": True
}

# Component validation schemas
COMPONENT_SCHEMAS = {
    "ui.hero": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "minLength": 1},
            "subtitle": {"type": "string"},
            "ctas": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "required": True},
                        "variant": {"type": "string", "enum": ["primary", "secondary", "outline"]}
                    }
                }
            }
        }
    },
    
    "ui.heading": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "minLength": 1, "required": True},
            "level": {"type": "integer", "minimum": 1, "maximum": 6, "default": 1},
            "size": {"type": "string", "enum": ["sm", "md", "lg", "xl"], "default": "lg"}
        }
    },
    
    "ui.text": {
        "type": "object", 
        "properties": {
            "text": {"type": "string", "minLength": 1, "required": True},
            "alignment": {"type": "string", "enum": ["left", "center", "right"], "default": "left"}
        }
    },
    
    "ui.button": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "minLength": 1, "required": True},
            "variant": {"type": "string", "enum": ["primary", "secondary", "outline"], "default": "primary"},
            "size": {"type": "string", "enum": ["sm", "md", "lg"], "default": "md"}
        }
    },
    
    "ui.form": {
        "type": "object",
        "properties": {
            "fields": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "required": True},
                        "label": {"type": "string", "required": True},
                        "type": {"type": "string", "enum": ["text", "email", "password", "textarea"], "default": "text"},
                        "required": {"type": "boolean", "default": False}
                    }
                }
            },
            "submitText": {"type": "string", "default": "Отправить"}
        }
    },
    
    "ui.card": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "text": {"type": "string"},
            "image": {"type": "string", "format": "uri"}
        }
    },
    
    "ui.container": {
        "type": "object",
        "properties": {
            "padding": {"type": "string", "enum": ["sm", "md", "lg", "xl"], "default": "md"},
            "children": {"type": "string", "default": "Container content"}
        }
    },
    
    "ui.footer": {
        "type": "object",
        "properties": {
            "columns": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "required": True},
                        "links": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
        }
    }
}

def validate_layout_structure(layout_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate layout structure using simple JSON Schema-like validation
    Returns (is_valid, list_of_errors)
    """
    errors = []
    
    try:
        # Check required fields
        if "template" not in layout_data:
            errors.append("Missing required field: template")
        elif not isinstance(layout_data["template"], str):
            errors.append("Field 'template' must be a string")
        elif layout_data["template"] not in ["hero-main-footer", "simple-main", "full-width"]:
            errors.append(f"Invalid template: {layout_data['template']}")
        
        if "sections" not in layout_data:
            errors.append("Missing required field: sections")
        elif not isinstance(layout_data["sections"], dict):
            errors.append("Field 'sections' must be an object")
        else:
            # Check sections structure
            required_sections = ["hero", "main", "footer"]
            for section_name in required_sections:
                if section_name not in layout_data["sections"]:
                    errors.append(f"Missing required section: {section_name}")
                elif not isinstance(layout_data["sections"][section_name], list):
                    errors.append(f"Section '{section_name}' must be an array")
            
            # Check component list limits
            section_limits = {"hero": 5, "main": 15, "footer": 10}
            for section_name, limit in section_limits.items():
                if section_name in layout_data["sections"]:
                    count = len(layout_data["sections"][section_name])
                    if count > limit:
                        errors.append(f"Section '{section_name}' has too many components: {count} > {limit}")
            
            # Validate individual components
            for section_name, components in layout_data["screensections"].items():
                if isinstance(components, list):
                    for i, component in enumerate(components):
                        component_errors = validate_component(component, f"{section_name}[{i}]")
                        errors.extend(component_errors)
        
        # Check count field
        if "count" in layout_data:
            if not isinstance(layout_data["count"], int) or layout_data["count"] < 0:
                errors.append("Field 'count' must be a non-negative integer")
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            logger.warning(f"Layout validation failed with {len(errors)} errors", extra={
                "event": "layout_validation_failed",
                "error_count": len(errors),
                "errors": errors,
                "service": "mod3_v1"
            })
        
        return is_valid, errors
        
    except Exception as e:
        error_msg = f"Layout validation error: {str(e)}"
        logger.error(error_msg, extra={
            "event": "layout_validation_error", 
            "error": str(e),
            "service": "mod3_v1"
        })
        return False, [error_msg]

def validate_component(component: Dict[str, Any], context: str = "") -> List[str]:
    """
    Validate individual component structure
    Returns list of validation errors
    """
    errors = []
    
    try:
        # Check component name
        if "component" not in component:
            errors.append(f"{context}: Missing 'component' field")
        elif not isinstance(component["component"], str):
            errors.append(f"{context}: Field 'component' must be a string")
        elif not component["component"].startswith("ui."):
            errors.append(f"{context}: Component name must start with 'ui.': {component['component']}")
        
        # Check props
        if "props" in component:
            if not isinstance(component["props"], dict):
                errors.append(f"{context}: Field 'props' must be an object")
            else:
                # Validate component-specific props
                component_name = component.get("component", "")
                if component_name in COMPONENT_SCHEMAS:
                    prop_errors = validate_component_props(
                        component["props"], 
                        COMPONENT_SCHEMAS[component_name],
                        context
                    )
                    errors.extend(prop_errors)
        
        # Check confidence score
        if "confidence" in component:
            confidence = component["confidence"]
            if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                errors.append(f"{context}: Field 'confidence' must be between 0.0 and 1.0")
        
        # Check match_type
        if "match_type" in component:
            valid_types = ["exact", "synonym", "fuzzy", "fallback"]
            if component["match_type"] not in valid_types:
                errors.append(f"{context}: Invalid match_type: {component['match_type']}")
        
        return errors
        
    except Exception as e:
        return [f"{context}: Component validation error: {str(e)}"]

def validate_component_props(props: Dict[str, Any], schema: Dict[str, Any], context: str = "") -> List[str]:
    """
    Basic validation of component properties against schema
    Returns list of validation errors
    """
    errors = []
    
    try:
        for prop_name, prop_config in schema.get("properties", {}).items():
            if prop_config.get("required", False) and prop_name not in props:
                errors.append(f"{context}: Missing required prop '{prop_name}'")
            elif prop_name in props:
                prop_value = props[prop_name]
                prop_type = prop_config.get("type")
                
                # Basic type checking
                if prop_type == "string" and not isinstance(prop_value, str):
                    errors.append(f"{context}: Prop '{prop_name}' must be a string")
                elif prop_type == "integer" and not isinstance(prop_value, int):
                    errors.append(f"{context}: Prop '{prop_name}' must be an integer")
                elif prop_type == "array" and not isinstance(prop_value, list):
                    errors.append(f"{context}: Prop '{prop_name}' must be an array")
                elif prop_type == "object" and not isinstance(prop_value, dict):
                    errors.append(f"{context}: Prop '{prop_name}' must be an object")
                
                # Enum validation
                if "enum" in prop_config:
                    if prop_value not in prop_config["enum"]:
                        errors.append(f"{context}: Prop '{prop_name}' must be one of {prop_config['enum']}")
                
                # String length validation
                if prop_type == "string" and isinstance(prop_value, str):
                    if "minLength" in prop_config and len(prop_value) < prop_config["minLength"]:
                        errors.append(f"{context}: Prop '{prop_name}' too short (min: {prop_config['minLength']})")
        
        return errors
        
    except Exception as e:
        return [f"{context}: Props validation error: {str(e)}"]

def ensure_default_component_values(component: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure component has default values for required fields
    """
    enhanced = component.copy()
    
    # Default values
    if "confidence" not in enhanced:
        enhanced["confidence"] = 0.5
    
    if "match_type" not in enhanced:
        enhanced["match_type"] = "fallback"
    
    if "props" not in enhanced:
        enhanced["props"] = {}
    
    # Component-specific defaults
    component_name = enhanced.get("component", "")
    if component_name in COMPONENT_SCHEMAS:
        schema = COMPONENT_SCHEMAS[component_name]
        for prop_name, prop_config in schema.get("properties", {}).items():
            if prop_name not in enhanced["props"] and "default" in prop_config:
                enhanced["props"][prop_name] = prop_config["default"]
    
    return enhanced
