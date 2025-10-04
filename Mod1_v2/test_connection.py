#!/usr/bin/env python3
"""
Тестовый скрипт для проверки связи между Mod1 и Mod2
Отправляет тестовый текст "Создайте кнопку для отправки формы" как будто он был записан в Mod1
"""

import asyncio
import json
import hmac
import hashlib
import httpx
import os
import uuid
from datetime import datetime

# Конфигурация
MOD1_URL = "http://localhost:8080"
MOD2_URL = "http://localhost:8000"
INGEST_SECRET = "changeme"

# Тестовый текст
TEST_TEXT = "Создайте кнопку для отправки формы"
SESSION_ID = f"test-{uuid.uuid4().hex[:8]}"

def create_signature(body: bytes, secret: str) -> str:
    """Создает HMAC-SHA256 подпись"""
    sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={sig}"

async def send_chunk_to_mod2(text: str, session_id: str, seq: int):
    """Отправляет чанк в Mod2"""
    chunk_data = {
        "session_id": session_id,
        "chunk_id": f"chunk-{seq}",
        "seq": seq,
        "text": text,
        "overlap_prefix": None,
        "lang": "ru-RU"
    }
    
    body = json.dumps(chunk_data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Signature": create_signature(body, INGEST_SECRET),
        "Idempotency-Key": f"{session_id}:chunk-{seq}",
        "X-Request-Id": f"{session_id}:{seq}",
    }
    
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(f"{MOD2_URL}/v2/ingest/chunk", content=body, headers=headers)
        return response

async def send_final_to_mod2(session_id: str, total_chunks: int):
    """Отправляет финальный результат в Mod2"""
    final_data = {
        "session_id": session_id,
        "text_full": TEST_TEXT,
        "lang": "ru-RU",
        "duration_sec": 5.0,
        "total_chunks": total_chunks
    }
    
    body = json.dumps(final_data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Signature": create_signature(body, INGEST_SECRET),
        "Idempotency-Key": f"{session_id}:final",
        "X-Request-Id": f"{session_id}:final",
    }
    
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(f"{MOD2_URL}/v2/ingest/full", content=body, headers=headers)
        return response

async def get_layout_from_mod2(session_id: str):
    """Получает layout из Mod2"""
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{MOD2_URL}/v2/session/{session_id}/layout")
        return response

async def main():
    print(f"🧪 Тестирование связи Mod1 → Mod2")
    print(f"📝 Тестовый текст: '{TEST_TEXT}'")
    print(f"🆔 Session ID: {SESSION_ID}")
    print("-" * 50)
    
    try:
        # 1. Отправляем чанк
        print("1️⃣ Отправляем чанк в Mod2...")
        chunk_response = await send_chunk_to_mod2(TEST_TEXT, SESSION_ID, 1)
        print(f"   Статус: {chunk_response.status_code}")
        if chunk_response.status_code == 200:
            print("   ✅ Чанк успешно отправлен")
        else:
            print(f"   ❌ Ошибка: {chunk_response.text}")
            return
        
        # 2. Отправляем финальный результат
        print("\n2️⃣ Отправляем финальный результат в Mod2...")
        final_response = await send_final_to_mod2(SESSION_ID, 1)
        print(f"   Статус: {final_response.status_code}")
        if final_response.status_code == 200:
            print("   ✅ Финальный результат успешно отправлен")
        else:
            print(f"   ❌ Ошибка: {final_response.text}")
            return
        
        # 3. Получаем layout
        print("\n3️⃣ Получаем layout из Mod2...")
        layout_response = await get_layout_from_mod2(SESSION_ID)
        print(f"   Статус: {layout_response.status_code}")
        if layout_response.status_code == 200:
            layout_data = layout_response.json()
            print("   ✅ Layout успешно получен:")
            print(f"   📋 Результат:")
            print(json.dumps(layout_data, ensure_ascii=False, indent=2))
        else:
            print(f"   ❌ Ошибка: {layout_response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")

if __name__ == "__main__":
    asyncio.run(main())