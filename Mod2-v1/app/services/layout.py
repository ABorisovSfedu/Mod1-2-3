from __future__ import annotations
from typing import Dict, List, Any
from config.settings import settings
from app.services.store import get_session_results
from app.services.tracing import log_event


# Простые правила раскладки по секциям для внутренней генерации
SECTION_RULES = {
    "ContactForm": "footer",
    "ServicesGrid": "main",
    "Button": "main",
    "Image": "main", 
    "Text": "main",
    "Hero": "hero",
    "Footer": "footer",
    "Navigation": "hero",
    "Welcome": "hero"
}


def build_layout_for_session(session_id: str) -> Dict[str, Any]:
    """
    Собираем layout из накопленных mappings в порядке seq, без дублей,
    ограничиваем MAX_COMPONENTS_PER_PAGE, укладываем по секциям шаблона.
    
    Теперь Mod2 НЕ вызывает Mod3 напрямую. Mod2 только извлекает entities/keyphrases,
    а веб-приложение должно получить их через /v2/session/{id}/entities 
    и передать в Mod3 для получения layout.
    """
    results = sorted(get_session_results(session_id), key=lambda r: r["seq"] or 0)
    seen = set()
    elements: List[str] = []
    
    # Собираем все элементы из mappings для простого fallback layout
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

    # Простая внутренняя логика раскладки (fallback)
    sections = {"hero": [], "main": [], "footer": []}
    
    # Добавляем Hero только если есть другие компоненты
    if elements and settings.page_template == "hero-main-footer":
        sections["hero"].append({"component": "Hero"})

    for elem in elements:
        sec = SECTION_RULES.get(elem, "main")
        sections[sec].append({"component": elem})

    # Логируем использование внутреннего провайдера
    log_event(
        "layout_provider_internal",
        service="module2",
        session_id=session_id,
        components_count=len(elements),
        note="Mod2 uses internal layout generation. Web app should call /entities and pass to Mod3."
    )

    return {
        "template": settings.page_template,
        "sections": sections,
        "count": sum(len(v) for v in sections.values()),
    }