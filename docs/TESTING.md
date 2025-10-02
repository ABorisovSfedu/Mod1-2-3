# Testing Guide for InterView Mod1-2-3 System

## Overview

This document provides comprehensive testing instructions for all modules in the InterView system. Each module can be tested independently and as part of the full integration flow.

## Prerequisites

- All modules must be running on their respective ports
- Environment variables configured (see `.env` files)
- Required dependencies installed

### Default Ports
- **Mod1_v2 (ASR)**: `8080`
- **Mod2-v1 (NLP)**: `8001` 
- **Mod3-v1 (Visual Mapping)**: `9001`

## Health Check Tests

### 1. Mod1_v2 Health Check
```bash
curl -X GET http://localhost:8080/healthz
```

**Expected Response:**
```json
{
  "status": "ok",
  "asr": "ready",
  "service": "Mod1_v2",
  "version": "1.0.0",
  "host": "0.0.0.0",
  "port": 8080,
  "timestamp": "2025-10-02T22:34:00.000Z"
}
```

### 2. Mod2-v1 Health Check
```bash
curl -X GET http://localhost:8001/healthz
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "Mod2-v1",
  "version": "1.0.0",
  "layout_provider": "external",
  "mod3_url": "http://localhost:9001",
  "nlp_debug": false,
  "feature_flags": {...}
}
```

### 3. Mod3-v1 Health Check
```bash
curl -X GET http://localhost:9001/healthz
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "Mod3-v1 - Visual Elements Mapping",
  "version": "1.0.0",
  "database_url": "sqlite:///./mod3.db",
  "feature_flags": {
    "require_props": true,
    "names_normalize": true,
    "dedup_by_component": true,
    "at_least_one_main": true,
    "fallback_sections": true,
    "max_matches": 6
  }
}
```

## Mod1_v2 (ASR) Testing

### 1. Audio Transcription Test
```bash
# Upload audio file for transcription
curl -X POST http://localhost:8080/v1/transcribe \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/audio.webm" \
  -F "session_id=test_session_001" \
  -F "lang=ru-RU"
```

**Test Audio Requirements:**
- Format: WebM, WAV, or MP3
- Duration: < 15 minutes
- Language: Russian (ru-RU)

**Expected Response:**
```json
{
  "session_id": "test_session_001",
  "text_full": "Полный текст транскрипции",
  "chunks": [
    {
      "session_id": "test_session_001",
      "chunk_id": "chunk_001",
      "seq": 1,
      "text": "Фрагмент текста",
      "lang": "ru-RU",
      "policy": {...},
      "hash": "abc123"
    }
  ]
}
```

### 2. ASR Logging Verification
Check that the ASR processes audio with proper timing logs:
```bash
# Look for these log entries in Mod1_v2 logs:
# "event": "asr_completed"
# "asr_duration_ms": <number>
# "file_size_bytes": <number>
```

## Mod2-v1 (NLP) Testing

### 1. Text Ingestion Test
```bash
curl -X POST http://localhost:8001/v2/ingest/chunk \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_001",
    "chunk_id": "chunk_001", 
    "seq": 1,
    "text": "Сделай сайт с кнопкой и заголовком",
    "lang": "ru-RU",
    "timestamp": 1759430000000
  }'
```

**Expected Response:**
```json
{
  "status": "ok",
  "session_id": "test_session_001",
  "chunk_id": "chunk_001",
  "timestamp": 1759430000000
}
```

### 2. Entities Extraction Test
```bash
curl -X GET http://localhost:8001/v2/session/test_session_001/entities
```

**Expected Response:**
```json
{
  "status": "ok",
  "session_id": "test_session_001",
  "entities": ["сайт", "кнопка", "заголовок"],
  "keyphrases": ["сайт", "кнопка", "заголовок"],
  "chunks_processed": 1
}
```

### 3. NLP Normalization Test (Debug Mode)
Enable NLP_DEBUG=true in environment and test normalization:
```bash
# Should show detailed NLP processing logs
curl -X POST http://localhost:8001/v2/ingest/chunk \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "debug_session_001",
    "chunk_id": "chunk_debug", 
    "seq": 1,
    "text": "Создайте красивый заголовок и кнопку отправки формы",
    "lang": "ru-RU",
    "timestamp": 1759430000000
  }'
```

### 4. Final Text Ingestion
```bash
curl -X POST http://localhost:8001/v2/ingest/full \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_001",
    "text_full": "Полный финальный текст для обработки",
    "lang": "ru-RU",
    "duration_sec": 120.5,
    "total_chunks": 3
  }'
```

## Mod3-v1 (Visual Mapping) Testing

### 1. Component Mapping Test
```bash
curl -X POST http://localhost:9001/v1/map \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_001",
    "entities": ["кнопка", "форма", "заголовок"],
    "keyphrases": ["кнопка отправки формы"],
    "template": "hero-main-footer"
  }'
```

**Expected Response:**
```json
{
  "status": "ok",
  "session_id": "test_session_001",
  "layout": {
    "template": "hero-main-footer",
    "sections": {
      "hero": [
        {
          "component": "ui.hero",
          "props": {
            "title": "Добро пожаловать",
            "subtitle": "Это демо сайт",
            "ctas": [
              {"text": "Начать", "variant": "primary"}
            ]
          },
          "confidence": 0.9,
          "match_type": "fallback",
          "term": "hero"
        }
      ],
      "main": [
        {
          "component": "ui.heading",
          "props": {
            "text": "Заголовок",
            "level": 1,
            "size": "xl"
          },
          "confidence": 0.9,
          "match_type": "exact",
          "term": "заголовок"
        },
        {
          "component": "ui.button",
          "props": {
            "text": "Отправить",
            "variant": "primary",
            "size": "md"
          },
          "confidence": 0.9,
          "match_type": "exact", 
          "term": "кнопка"
        }
      ],
      "footer": []
    },
    "count": 3
  },
  "matches": [...],
  "explanations": [
    {
      "term": "заголовок",
      "matched_component": "ui.heading", 
      "match_type": "exact",
      "score": 0.9
    }
  ]
}
```

### 2. Component Catalog Test
```bash
curl -X GET http://localhost:9001/v1/components
```

**Expected Response:**
```json
{
  "status": "ok",
  "components": [
    {
      "name": "ui.hero",
      "category": "branding",
      "tags": ["hero", "welcome", "splash"],
      "props_schema": {...},
      "example_props": {...},
      "min_span": 12,
      "max_span": 12
    }
  ]
}
```

### 3. Layout Retrieval Test
```bash
curl -X GET http://localhost:9001/v1/layout/test_session_001
```

### 4. Feature Flags Testing

**Test Name Normalization (M3_NAMES_NORMALIZE=true):**
```bash
# Should convert "Hero" -> "ui.hero"
curl -X POST http://localhost:9001/v1/map \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_normalize",
    "entities": ["герой"],
    "keyphrases": ["Hero"],
    "template": "hero-main-footer"
  }'
```

**Test Required Props (M3_REQUIRE_PROPS=true):**
- All components should have proper `props` objects
- Check that empty props are filled with example values

**Test Deduplication (M3_DEDUP_BY_COMPONENT=true):**
```bash
# Test with duplicate terms
curl -X POST http://localhost:9001/v1/map \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_dedup",
    "entities": ["кнопка", "кнопка", "кнопка"],
    "keyphrases": ["кнопка отправки формы", "кнопка"],
    "template": "hero-main-footer"
  }'
```

**Test Main Section Requirement (M3_AT_LEAST_ONE_MAIN=true):**
```bash
# Test empty main section - should add ui.container
curl -X POST http://localhost:9001/v1/map \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_empty_main",
    "entities": [],
    "keyphrases": [],
    "template": "hero-main-footer"
  }'
```

**Test Fallback Sections (M3_FALLBACK_SECTIONS=true):**
- Should return fallback layout when no matches found
- Should include ui.hero and ui.container by default

**Test Match Limiting (M3_MAX_MATCHES=6):**
```bash
# Test with many terms - should limit to 6 matches
curl -X POST http://localhost:9001/v1/map \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_limit",
    "entities": ["термин1", "термин2", "термин3", "термин4", "термин5", "термин6", "термин7", "термин8"],
    "keyphrases": ["много терминов для тестирования"],
    "template": "hero-main-footer"
  }'
```

## Integration Testing (Full Flow)

### 1. Complete Workflow Test
```bash
#!/bin/bash
# Test complete Mod1 -> Mod2 -> Mod3 flow

# 1. Ensure all modules are healthy
echo "=== Health Checks ==="
curl -s http://localhost:8080/healthz | jq '.status'
curl -s http://localhost:8001/healthz | jq '.status'  
curl -s http://localhost:9001/healthz | jq '.status'

# 2. Send text to Mod2
echo "=== Sending text to Mod2 ==="
curl -X POST http://localhost:8001/v2/ingest/chunk \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "integration_test_001",
    "chunk_id": "chunk_001",
    "seq": 1,
    "text": "Сделай сайт с заголовком и кнопкой отправки формы",
    "lang": "ru-RU",
    "timestamp": 1759430000000
  }'

# 3. Get entities from Mod2
echo "=== Getting entities from Mod2 ==="
ENTITIES=$(curl -s http://localhost:8001/v2/session/integration_test_001/entities | jq -r '.entities | join(",")')
KEYPHRASES=$(curl -s http://localhost:8001/v2/session/integration_test_001/entities | jq -r '.keyphrases | join(",")')

echo "Extracted entities: $ENTITIES"
echo "Extracted keyphrases: $KEYPHRASES"

# 4. Send to Mod3 for layout generation
echo "=== Sending to Mod3 ==="
curl -X POST http://localhost:9001/v1/map \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"integration_test_001\",
    \"entities\": [\"$(echo $ENTITIES | sed 's/,/", "/g')\"],
    \"keyphrases\": [\"$(echo $KEYPHRASES | sed 's/,/", "/g')\"],
    \"template\": \"hero-main-footer\"
  }" | jq '.layout'
```

### 2. Success Criteria Validation

For a successful layout generation with text "Сделай сайт с заголовком и кнопкой отправки формы":

**Mod3 Response Should Include:**
- ✅ `template`: "hero-main-footer"
- ✅ `hero` section: Contains `ui.hero` component with proper props
- ✅ `main` section: Contains `ui.heading` and `ui.button` components  
- ✅ All components have `props` objects (not empty)
- ✅ Component names use `ui.*` format
- ✅ `confidence` scores between 0.0-1.0
- ✅ `match_type` values are valid
- ✅ `explanations` array included
- ✅ `count` > 0

**Expected Components:**
```json
{
  "layout": {
    "template": "hero-main-footer",
    "sections": {
      "hero": [
        {
          "component": "ui.hero",
          "props": {
            "title": "Добро пожаловать",
            "subtitle": "Это демо сайт",
            "ctas": [{"text": "Начать", "variant": "primary"}]
          },
          "confidence": 0.9,
          "match_type": "fallback"
        }
      ],
      "main": [
        {
          "component": "ui.heading",
          "props": {
            "text": "Заголовок",
            "level": 1,
            "size": "xl"
          },
          "confidence": 0.9,
          "match_type": "exact",
          "term": "заголовок"
        },
        {
          "component": "ui.button", 
          "props": {
            "text": "Отправить",
            "variant": "primary",
            "size": "md"
          },
          "confidence": 0.9,
          "match_type": "exact",
          "term": "кнопка"
        }
      ],
      "footer": []
    },
    "count": 3
  }
}
```

## Error Testing

### 1. Invalid Session IDs
```bash
# Test non-existent session
curl -X GET http://localhost:8001/v2/session/nonexistent/entities
curl -X GET http://localhost:9001/v1/layout/nonexistent
```

### 2. Empty/Malformed Requests
```bash
# Test empty entities
curl -X POST http://localhost:9001/v1/map \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "empty_test",
    "entities": [],
    "keyphrases": [],
    "template": "hero-main-footer"
  }'
```

### 3. Invalid Templates
```bash
# Test invalid template
curl -X POST http://localhost:9001/v1/map \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "invalid_template_test",
    "entities": ["кнопка"],
    "keyphrases": [],
    "template": "invalid-template"
  }'
```

## Performance Testing

### 1. Concurrent Requests
```bash
# Run multiple requests simultaneously
for i in {1..10}; do
  curl -X POST http://localhost:8001/v2/ingest/chunk \
    -H "Content-Type: application/json" \
    -d "{\"session_id\": \"perf_test_$i\", \"chunk_id\": \"chunk_$i\", \"seq\": 1, \"text\": \"Тест производительности $i\", \"lang\": \"ru-RU\", \"timestamp\": 1759430000000}"
done
```

### 2. Large Text Processing
```bash
# Test with large text
curl -X POST http://localhost:8001/v2/ingest/chunk \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"large_text_test\",
    \"chunk_id\": \"chunk_large\", 
    \"seq\": 1,
    \"text\": \"$(python3 -c 'print("Большой текст для тестирования " * 1000)')\&" -H \"Content-Type: application/json\"),
    \"lang\": \"ru-RU\",
    \"timestamp\": 1759430000000
  }"
```

## Debugging

### Log Analysis
- **Mod1_v2**: Look for `asr_start_time`, `asr_duration_ms`, `delivery_started`
- **Mod2-v1**: Look for `chunk_received`, `chunk_processed`, `entities_endpoint`
- **Mod3-v1**: Look for `mapping_request`, `mapping_completed`, `layout_validation`

### Common Issues

1. **"503 Service Unavailable"**: Check if all modules are running on correct ports
2. **"Empty entities"**: Verify NLP processing is working in Mod2
3. **"Empty layout"**: Check Mod3 database initialization with enhanced script
4. **"Invalid component names"**: Ensure M3_NAMES_NORMALIZE=true is set

### Useful Commands

```bash
# Check if ports are in use
lsof -i :8080
lsof -i :8001  
lsof -i :9001

# Check module logs
tail -f Mod1_v2/logs/app.log
tail -f Mod2-v1/logs/app.log
tail -f Mod3-v1/logs/app.log

# Test with curl verbose
curl -v -X GET http://localhost:9001/healthz

# Check environment variables
env | grep -E "(MOD1_|MOD2_|MOD3_|M3_)"
```

## Automated Testing Setup

Consider setting up automated tests using:
- **Postman collections** for API testing
- **Newman** for CLI testing  
- **Jenkins/GitHub Actions** for CI/CD
- **JMeter** for performance testing

## Test Data Requirements

Maintain test datasets with:
- Sample Russian audio files
- Known text inputs and expected outputs
- Component catalog snapshots
- Performance benchmarks

## Success Metrics

System is ready for production when:
- ✅ All health checks return 200 OK
- ✅ End-to-end flow completes within 10 seconds
- ✅ Mod3 returns valid layouts with components > 0
- ✅ All feature flags work as expected
- ✅ Error handling works gracefully
- ✅ Performance is within acceptable limits
