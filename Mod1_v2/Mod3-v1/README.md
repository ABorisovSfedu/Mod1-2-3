# Mod3-v1 - Visual Elements Mapping Service

Микросервис для сопоставления NLP результатов с визуальными элементами интерфейса.

## Описание

Mod3-v1 принимает от Mod2-v1 результаты NLP (ключевые слова, сущности, session_id), сопоставляет их с библиотекой визуальных элементов и возвращает готовый layout в формате JSON.

## Возможности

- **Сопоставление терминов**: Точное совпадение, поиск по синонимам, fuzzy matching с RapidFuzz
- **Генерация layout'ов**: Создание структурированных layout'ов по шаблонам
- **Управление словарем**: CRUD операции с терминами, синонимами и компонентами
- **Хранение результатов**: Сохранение layout'ов в PostgreSQL
- **REST API**: Полноценный REST API с документацией

## Архитектура

### База данных

- **terms** - Словарь терминов
- **synonyms** - Синонимы терминов
- **components** - Визуальные компоненты
- **mappings** - Сопоставления терминов с компонентами
- **templates** - Шаблоны layout'ов
- **layouts** - Сохраненные layout'ы

### API Endpoints

#### Основные
- `POST /v1/map` - Сопоставление сущностей с layout'ом
- `GET /v1/layout/{session_id}` - Получение сохраненного layout'а

#### Словарь
- `GET /v1/vocab` - Получение всего словаря
- `POST /v1/vocab/sync` - Синхронизация словаря

#### Системные
- `GET /healthz` - Проверка состояния сервиса

## Установка и запуск

### Docker Compose (рекомендуется)

```bash
# Запуск всех сервисов
docker-compose up --build -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f mod3-app
```

### Локальная разработка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка базы данных
export DATABASE_URL="postgresql://mod3_user:mod3_password@localhost:5433/mod3_db"

# Инициализация данных
python scripts/init_data.py

# Запуск приложения
python main.py
```

## Использование

### Пример запроса к /v1/map

```bash
curl -X POST http://localhost:9000/v1/map \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "entities": ["кнопка", "форма"],
    "keyphrases": ["создайте кнопку для отправки"],
    "template": "hero-main-footer"
  }'
```

### Пример ответа

```json
{
  "status": "ok",
  "session_id": "test_session",
  "layout": {
    "template": "hero-main-footer",
    "sections": {
      "hero": [{"component": "Hero", "confidence": 1.0, "match_type": "default"}],
      "main": [
        {"component": "ui.button", "confidence": 1.0, "match_type": "exact"},
        {"component": "ui.form", "confidence": 1.0, "match_type": "exact"}
      ],
      "footer": []
    },
    "count": 3
  },
  "matches": [
    {
      "term": "кнопка",
      "component": "ui.button",
      "component_type": "ui.button",
      "confidence": 1.0,
      "match_type": "exact"
    },
    {
      "term": "форма",
      "component": "ui.form", 
      "component_type": "ui.form",
      "confidence": 1.0,
      "match_type": "exact"
    }
  ]
}
```

## Алгоритм сопоставления

1. **Точное совпадение**: Поиск точного совпадения термина в базе
2. **Поиск по синонимам**: Поиск среди синонимов терминов
3. **Fuzzy matching**: Использование RapidFuzz с порогом 0.8
4. **Дедупликация**: Удаление дубликатов по компонентам
5. **Сортировка**: Сортировка по уверенности (confidence)

## Конфигурация

Основные настройки в `config/settings.py`:

- `fuzzy_threshold` - Порог для fuzzy matching (по умолчанию 0.8)
- `max_components_per_section` - Максимум компонентов на секцию
- `default_template` - Шаблон по умолчанию
- `cors_origins` - Разрешенные CORS origins

## Порты

- **Mod3-v1**: 9000
- **PostgreSQL**: 5433

## Интеграция с другими модулями

Mod3-v1 предназначен для работы с Mod2-v1:

1. Mod2-v1 отправляет NLP результаты в Mod3-v1
2. Mod3-v1 сопоставляет их с визуальными элементами
3. Возвращает готовый layout для фронтенда

## Разработка

### Структура проекта

```
Mod3-v1/
├── app/
│   ├── models/          # Модели SQLAlchemy
│   ├── routers/         # API роутеры
│   ├── services/        # Бизнес-логика
│   └── utils/           # Утилиты
├── alembic/             # Миграции базы данных
├── config/              # Конфигурация
├── scripts/             # Скрипты инициализации
├── docker-compose.yml   # Docker Compose
├── Dockerfile          # Docker образ
└── main.py             # Точка входа
```

### Добавление новых компонентов

1. Добавить компонент в базу данных
2. Создать маппинги с терминами
3. Обновить правила шаблонов при необходимости

### Добавление новых шаблонов

1. Создать новый Template в базе данных
2. Определить структуру секций
3. Настроить правила размещения компонентов

