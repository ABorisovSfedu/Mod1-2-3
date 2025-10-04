import os, json, time, random, hmac, hashlib
import httpx
from typing import Dict, Any, Optional

CHUNK_URL = os.getenv("MODULE2_WEBHOOK_CHUNK_URL", "http://module2:8000/v2/ingest/chunk")
FINAL_URL = os.getenv("MODULE2_WEBHOOK_FINAL_URL", "http://module2:8000/v2/ingest/full")
INGEST_SECRET = os.getenv("INGEST_SECRET", "changeme")
RETRIES = int(os.getenv("DELIVERY_RETRIES", "5"))
BACKOFF_BASE_MS = int(os.getenv("DELIVERY_BACKOFF_BASE_MS", "500"))

def _signature(body: bytes) -> str:
    sig = hmac.new(INGEST_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={sig}"

async def _post_json(url: str, payload: Dict[str, Any], idem_key: str) -> httpx.Response:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Signature": _signature(body),
        "Idempotency-Key": idem_key,
        "X-Request-Id": f"{payload['session_id']}:{payload.get('seq', 'final')}",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        return await client.post(url, content=body, headers=headers)

async def _deliver_with_retries(url: str, payload: Dict[str, Any], idem_key: str):
    for attempt in range(RETRIES + 1):
        try:
            resp = await _post_json(url, payload, idem_key)
            if resp.status_code >= 500:
                raise RuntimeError(f"server_{resp.status_code}")
            if resp.status_code == 429:
                delay = (BACKOFF_BASE_MS / 1000.0) * (2 ** attempt) + random.uniform(0, 0.5)
                await _sleep(delay * 2)
                continue
            if 400 <= resp.status_code < 500:
                return resp
            return resp
        except Exception:
            # таймаут/сетевые/5xx
            delay = (BACKOFF_BASE_MS / 1000.0) * (2 ** attempt) + random.uniform(0, 0.5)
            await _sleep(delay)
    class _Fail:
        status_code = 503
        text = "delivery failed after retries"
    return _Fail()

async def _sleep(sec: float):
    # заменить на asyncio.sleep, если у тебя async контекст
    import asyncio; await asyncio.sleep(sec)

async def deliver_chunk(chunk: Dict[str, Any]):
    idem_key = f"{chunk['session_id']}:{chunk['chunk_id']}"
    return await _deliver_with_retries(CHUNK_URL, chunk, idem_key)

async def deliver_final(final: Dict[str, Any]):
    idem_key = f"{final['session_id']}:final"
    return await _deliver_with_retries(FINAL_URL, final, idem_key)
