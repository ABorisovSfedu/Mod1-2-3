from __future__ import annotations
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import json
from ..services.sessions import SESSION_MANAGER

router = APIRouter()

@router.websocket("/v1/stream")
async def ws_stream(
    ws: WebSocket,
    session_id: str = Query(...),
    lang: str = Query("ru-RU"),
    emit_partial: bool = Query(True),
    chunking: str = Query("on"),
):
    await ws.accept()
    await ws.send_text(json.dumps({"type": "hello", "session_id": session_id}))
    try:
        while True:
            msg = await ws.receive()
            if "bytes" in msg and msg["bytes"]:
                await SESSION_MANAGER.append_audio(session_id, lang, msg["bytes"])
                await ws.send_text(json.dumps({"type": "progress", "session_id": session_id}))
            elif "text" in msg and msg["text"]:
                try:
                    payload = json.loads(msg["text"])
                except Exception:
                    payload = {"type": "text", "value": msg["text"]}
                if payload.get("type") == "eos":
                    final = await SESSION_MANAGER.close_session(session_id, lang)
                    await ws.send_text(json.dumps({"type": "final_full", "payload": final}, ensure_ascii=False))
                    await ws.close()
                    break
            else:
                pass
    except WebSocketDisconnect:
        await SESSION_MANAGER.close_session(session_id, lang)