from __future__ import annotations
import hmac, hashlib, json
import httpx
from typing import Optional
from sqlmodel import select
from ..db import get_session
from ..models import WebhookModel

HEADER_NAME = "X-Signature"

async def get_active_webhook() -> Optional[WebhookModel]:
    with get_session() as s:
        wh = s.exec(select(WebhookModel).where(WebhookModel.active == True)).first()  # noqa: E712
        return wh

async def set_webhook(url: str, secret: str) -> WebhookModel:
    with get_session() as s:
        wh = s.exec(select(WebhookModel).where(WebhookModel.active == True)).first()  # noqa: E712
        if wh:
            wh.url = url
            wh.secret = secret
        else:
            wh = WebhookModel(url=url, secret=secret, active=True)
            s.add(wh)
        s.commit(); s.refresh(wh)
        return wh

async def send_chunk(webhook: WebhookModel, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    sig = hmac.new(webhook.secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    async with httpx.AsyncClient(timeout=5.0) as client:
        await client.post(webhook.url, content=body, headers={HEADER_NAME: f"sha256={sig}", "Content-Type": "application/json"})