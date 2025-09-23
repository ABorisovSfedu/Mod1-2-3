# Module 2: NLP → Key Phrases → Mapping → Layout (FastAPI, Python 3.11)

MVP микросервиса:
- Stanza (ru) для разбиения и лемматизации
- Извлечение простых NP (NOUN, ADJ+NOUN, NOUN+NOUN)
- Фильтрация, confidence (0.8/0.6), дедупликация
- Маппинг на онтологию (точное + fuzzy RapidFuzz)
- Сборка layout по шаблону `hero-main-footer`
- Конфиг: ENV и `config/app.yaml`
- Тарифы: BASIC / EXTENDED / PREMIUM

## Конфигурация (ENV или `config/app.yaml`)
- `STANZA_LANG` (default `ru`)
- `FUZZY_THRESHOLD` (default `0.80`)
- `STREAM_PREVIEW` (default `true`)
- `PAGE_TEMPLATE` (default `hero-main-footer`)
- `MAX_COMPONENTS_PER_PAGE` (default `12`)
- `PLAN` (default `EXTENDED`; варианты: `BASIC`, `EXTENDED`, `PREMIUM`)

Пример `config/app.yaml`:
```yaml
STANZA_LANG: ru
FUZZY_THRESHOLD: 0.80
STREAM_PREVIEW: true
PAGE_TEMPLATE: hero-main-footer
MAX_COMPONENTS_PER_PAGE: 12
PLAN: EXTENDED
# module2
