#!/usr/bin/env python3
"""
Seed script to populate the database with UI components
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Component

def seed_components():
    """Add UI components to the database"""
    
    # Get database session
    db = next(get_db())
    
    components_data = [
        {
            "name": "ui.hero",
            "component_type": "ui.hero",
            "description": "Hero section component for landing pages",
            "category": "branding",
            "props_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "subtitle": {"type": "string"},
                    "backgroundImage": {"type": "string"},
                    "ctaText": {"type": "string"},
                    "ctaLink": {"type": "string"}
                },
                "required": ["title"]
            },
            "example_props": {
                "title": "Welcome to Our Platform",
                "subtitle": "Build amazing applications with ease",
                "backgroundImage": "/images/hero-bg.jpg",
                "ctaText": "Get Started",
                "ctaLink": "/signup"
            },
            "min_span": 12,
            "max_span": 12
        },
        {
            "name": "ui.container",
            "component_type": "ui.container",
            "description": "Container component for layout structure",
            "category": "action",
            "props_schema": {
                "type": "object",
                "properties": {
                    "maxWidth": {"type": "string", "enum": ["sm", "md", "lg", "xl", "full"]},
                    "padding": {"type": "string"},
                    "backgroundColor": {"type": "string"},
                    "className": {"type": "string"}
                }
            },
            "example_props": {
                "maxWidth": "lg",
                "padding": "4",
                "backgroundColor": "white",
                "className": "container"
            },
            "min_span": 1,
            "max_span": 12
        },
        {
            "name": "ui.button",
            "component_type": "ui.button",
            "description": "Button component for user interactions",
            "category": "action",
            "props_schema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "variant": {"type": "string", "enum": ["primary", "secondary", "outline", "ghost"]},
                    "size": {"type": "string", "enum": ["sm", "md", "lg"]},
                    "onClick": {"type": "string"},
                    "disabled": {"type": "boolean"},
                    "href": {"type": "string"}
                },
                "required": ["text"]
            },
            "example_props": {
                "text": "Click Me",
                "variant": "primary",
                "size": "md",
                "onClick": "handleClick",
                "disabled": False
            },
            "min_span": 1,
            "max_span": 4
        },
        {
            "name": "ui.text",
            "component_type": "ui.text",
            "description": "Text component for displaying content",
            "category": "action",
            "props_schema": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "variant": {"type": "string", "enum": ["h1", "h2", "h3", "h4", "h5", "h6", "p", "span"]},
                    "color": {"type": "string"},
                    "align": {"type": "string", "enum": ["left", "center", "right", "justify"]},
                    "className": {"type": "string"}
                },
                "required": ["content"]
            },
            "example_props": {
                "content": "This is a sample text",
                "variant": "p",
                "color": "gray.700",
                "align": "left",
                "className": "text-base"
            },
            "min_span": 1,
            "max_span": 12
        },
        {
            "name": "ui.form",
            "component_type": "ui.form",
            "description": "Form component for user input",
            "category": "form",
            "props_schema": {
                "type": "object",
                "properties": {
                    "fields": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "label": {"type": "string"},
                                "required": {"type": "boolean"},
                                "placeholder": {"type": "string"}
                            }
                        }
                    },
                    "onSubmit": {"type": "string"},
                    "submitText": {"type": "string"},
                    "className": {"type": "string"}
                },
                "required": ["fields"]
            },
            "example_props": {
                "fields": [
                    {
                        "name": "email",
                        "type": "email",
                        "label": "Email Address",
                        "required": True,
                        "placeholder": "Enter your email"
                    },
                    {
                        "name": "name",
                        "type": "text",
                        "label": "Full Name",
                        "required": True,
                        "placeholder": "Enter your name"
                    }
                ],
                "onSubmit": "handleSubmit",
                "submitText": "Submit",
                "className": "form-container"
            },
            "min_span": 6,
            "max_span": 12
        },
        {
            "name": "ui.card",
            "component_type": "ui.card",
            "description": "Card component for content display",
            "category": "card",
            "props_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "image": {"type": "string"},
                    "actions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"},
                                "onClick": {"type": "string"}
                            }
                        }
                    },
                    "className": {"type": "string"}
                }
            },
            "example_props": {
                "title": "Card Title",
                "content": "This is the card content with some description.",
                "image": "/images/card-image.jpg",
                "actions": [
                    {
                        "text": "Learn More",
                        "onClick": "handleLearnMore"
                    }
                ],
                "className": "card-container"
            },
            "min_span": 3,
            "max_span": 6
        }
    ]
    
    try:
        for component_data in components_data:
            # Check if component already exists
            existing = db.query(Component).filter(
                Component.component_type == component_data["component_type"]
            ).first()
            
            if not existing:
                component = Component(**component_data)
                db.add(component)
                print(f"Added component: {component_data['component_type']}")
            else:
                print(f"Component already exists: {component_data['component_type']}")
        
        db.commit()
        print("Successfully seeded components!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding components: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_components()

