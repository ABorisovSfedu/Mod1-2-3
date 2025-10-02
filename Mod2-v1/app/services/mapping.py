from __future__ import annotations
from pathlib import Path
import json
from typing import List, Dict, Any
from rapidfuzz import fuzz

from app.models.schemas import Keyphrase, MappingResult
from config.settings import settings

BASE_DIR = Path(__file__).resolve().parents[2]
VOCAB_PATH = BASE_DIR / "config" / "vocab.json"


def _default_vocab() -> Dict[str, Any]:
    return {
        "vocab_version": "0.1.1",
        "terms": [
            {
                "lemma": "форма обратный связь",
                "aliases": ["форма обратной связи", "обратная связь", "форма связи", "contact form"],
                "element": "ContactForm"
            },
            {
                "lemma": "каталог услуга",
                "aliases": ["каталог услуг", "каталог сервисов", "services catalog", "список услуг"],
                "element": "ServicesGrid"
            },
            {"lemma": "форма", "aliases": ["form"], "element": "ContactForm"}
        ],
    }


def load_vocab() -> Dict[str, Any]:
    if not VOCAB_PATH.exists():
        return _default_vocab()
    try:
        return json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    except Exception:
        return _default_vocab()


def map_keyphrases_to_elements(keyphrases: List[Keyphrase], fuzzy_threshold: float | None = None) -> List[MappingResult]:
    vocab = load_vocab()
    terms = vocab.get("terms", [])
    out: List[MappingResult] = []

    threshold = settings.fuzzy_threshold if fuzzy_threshold is None else fuzzy_threshold

    # Готовим варианты сопоставлений
    term_variants: List[Dict[str, Any]] = []
    for t in terms:
        lemma = (t.get("lemma") or "").lower().strip()
        aliases = [(a or "").lower().strip() for a in t.get("aliases", [])]
        element = t.get("element")
        strings = [s for s in [lemma, *aliases] if s]
        if not element or not strings:
            continue
        term_variants.append({"element": element, "strings": strings})

    for kp in keyphrases:
        k = kp.lemma.lower().strip()
        # 1) Точное совпадение
        exact_hit = None
        for tv in term_variants:
            if k in tv["strings"]:
                exact_hit = MappingResult(keyphrase=kp, element=tv["element"], score=1.0)
                out.append(exact_hit)
                break
        if exact_hit:
            continue

        # 2) Fuzzy
        best_score = 0.0
        best_element = None
        for tv in term_variants:
            for s in tv["strings"]:
                score = fuzz.ratio(k, s) / 100.0
                if score > best_score:
                    best_score = score
                    best_element = tv["element"]
        if best_element and best_score >= threshold:
            out.append(MappingResult(keyphrase=kp, element=best_element, score=best_score))

    return out


def process_text_mapping(text: str) -> List[MappingResult]:
    """
    Обрабатывает текст и создает маппинги на UI компоненты.
    Использует NLP pipeline для извлечения ключевых фраз и сопоставления с элементами.
    """
    from app.nlp.extract import extract_keyphrases
    
    # Извлекаем ключевые фразы из текста
    keyphrases = extract_keyphrases(text)
    
    # Сопоставляем ключевые фразы с элементами
    mappings = map_keyphrases_to_elements(keyphrases)
    
    return mappings
