from __future__ import annotations
from typing import Dict, List, Any
from config.settings import settings
from app.services.store import get_session_results


# Простые правила раскладки по секциям
SECTION_RULES = {
    "ContactForm": "footer",
    "ServicesGrid": "main",
}


def build_layout_for_session(session_id: str) -> Dict[str, Any]:
    """
    Собираем layout из накопленных mappings в порядке seq, без дублей,
    ограничиваем MAX_COMPONENTS_PER_PAGE, укладываем по секциям шаблона.
    """
    results = sorted(get_session_results(session_id), key=lambda r: r["seq"] or 0)
    seen = set()
    elements: List[str] = []
    for rec in results:
        for m in rec.get("mappings", []):
            elem = m.get("element")
            if not elem:
                continue
            if elem not in seen:
                seen.add(elem)
                elements.append(elem)

    # Ограничение количества компонентов на страницу
    elements = elements[: settings.max_components_per_page]

    sections = {"hero": [], "main": [], "footer": []}
    # Добавляем Hero только если есть другие компоненты
    if elements and settings.page_template == "hero-main-footer":
        sections["hero"].append({"component": "Hero"})

    for elem in elements:
        sec = SECTION_RULES.get(elem, "main")
        sections[sec].append({"component": elem})

    return {
        "template": settings.page_template,
        "sections": sections,
        "count": sum(len(v) for v in sections.values()),
    }
