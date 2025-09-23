from fastapi import APIRouter
from app.services.layout import build_layout_for_session

router = APIRouter(prefix="/v2/session", tags=["session"])


@router.get("/{session_id}/layout")
def get_session_layout(session_id: str):
    layout = build_layout_for_session(session_id)
    return {"status": "ok", "session_id": session_id, "layout": layout}
