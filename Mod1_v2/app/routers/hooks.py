from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from ..services.webhooks import set_webhook

router = APIRouter(prefix="/v1/hook")

class HookIn(BaseModel):
    url: str
    secret: str

@router.post("/module2")
async def register_hook(body: HookIn):
    wh = await set_webhook(body.url, body.secret)
    return {"url": wh.url, "active": wh.active}