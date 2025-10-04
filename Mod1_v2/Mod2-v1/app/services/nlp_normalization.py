"""
NLP normalization service for Mod2-v1
Provides clean entities and keyphrases for Mod3 integration
"""
from __future__ import annotations
from typing import List, Dict, Set, Tuple
import logging
import os
from app.nlp.extract import extract_keyphrases

logger = logging.getLogger(__name__)

def normalize_text_to_lower(text: str) -> str:
    """Normalize text to lowercase and remove extra whitespace"""
    return text.strip().lower()

def deduplicate_list(items: List[str]) -> List[str]:
    """Remove duplicates while preserving order"""
    seen = set()
    result = []
    for item in items:
        normalized = normalize_text_to_lower(item)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result

def extract_and_normalize_entities(text: str) -> Tuple[List[str], List[str]]:
    """
    Extract entities and keyphrases from text and normalize them.
    Returns (entities, keyphrases) where both are normalized and deduplicated.
    """
    if not text or not text.strip():
        return [], []
    
    try:
        # Extract keyphrases using existing NLP pipeline
        keyphrases = extract_keyphrases(text)
        
        # Separate entities (singular terms) and keyphrases (multi-word phrases)
        entities = []
        normalized_keyphrases = []
        
        for kp in keyphrases:
            if kp.text:
                normalized_text = normalize_text_to_lower(kp.text)
                if normalized_text:
                    # Single words or lemmas are entities
                    if kp.lemma and not ' ' in kp.lemma.strip():
                        entities.append(normalized_text)
                    else:
                        normalized_keyphrases.append(normalized_text)
        
        # Deduplicate both lists
        entities = deduplicate_list(entities)
        normalized_keyphrases = deduplicate_list(normalized_keyphrases)
        
        # Log extracted data (safely, without PII)
        logger.debug("NLP extraction completed", extra={
            "event": "nlp_extraction",
            "text_length": len(text),
            "entities_count": len(entities),
            "keyphrases_count": len(normalized_keyphrases),
            "service": "mod2_v1"
        })
        
        return entities, normalized_keyphrases
        
    except Exception as e:
        logger.error(f"NLP extraction failed: {str(e)}", extra={
            "event": "nlp_extraction_error",
            "error": str(e),
            "text_length": len(text) if text else 0,
            "service": "mod2_v1"
        })
        return [], []

def format_mod3_payload(session_id: str, entities: List[str], keyphrases: List[str]) -> Dict[str, any]:
    """
    Format payload for Mod3 /v1/map endpoint.
    Ensures all required fields are present and normalized.
    """
    # Read Mod3 configuration from environment
    mod3_url = os.getenv("MOD3_URL", "http://localhost:9001")
    template = os.getenv("PAGE_TEMPLATE", "hero-main-footer")
    
    payload = {
        "session_id": session_id,
        "entities": entities,
        "keyphrases": keyphrases, 
        "template": template
    }
    
    logger.info("Formatted Mod3 payload", extra={
        "event": "mod3_payload_formatted",
        "session_id": session_id,
        "entities_count": len(entities),
        "keyphrases_count": len(keyphrases),
        "template": template,
        "service": "mod2_v1"
    })
    
    return payload

def validate_mod3_response(response_data: Dict[str, any], session_id: str) -> Dict[str, any]:
    """
    Validate Mod3 response and provide safe logging.
    Returns validated response or logs warnings for empty sections.
    """
    if not response_data:
        logger.warning("Mod3 returned empty response", extra={
            "event": "mod3_empty_response",
            "session_id": session_id,
            "service": "mod2_v1"
        })
        return {}
    
    # Extract layout information safely
    layout = response_data.get("layout", {})
    sections = layout.get("sections", {})
    
    # Count components in each section
    hero_count = len(sections.get("hero", []))
    main_count = len(sections.get("main", []))
    footer_count = len(sections.get("footer", []))
    total_count = hero_count + main_count + footer_count
    
    # Log response details (without exposing sensitive data)
    logger.info("Mod3 response validated", extra={
        "event": "mod3_response_validated", 
        "session_id": session_id,
        "template": layout.get("template", "unknown"),
        "hero_count": hero_count,
        "main_count": main_count, 
        "footer_count": footer_count,
        "total_components": total_count,
        "service": "mod2_v1"
    })
    
    # Check for empty main section (warning, not error)
    if main_count == 0 and total_count > 0:
        logger.warning("Mod3 layout has empty main section", extra={
            "event": "mod3_empty_main_section",
            "session_id": session_id,
            "total_components": total_count,
            "service": "mod2_v1"
        })
    
    # Check for completely empty response
    if total_count == 0:
        logger.warning("Mod3 layout is completely empty, fallback may be needed", extra={
            "event": "mod3_empty_layout",
            "session_id": session_id,
            "service": "mod2_v1"
        })
    
    return response_data
