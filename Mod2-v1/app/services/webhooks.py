from typing import Optional, Dict, Any

async def get_secret_for_session(session_id: Optional[str]) -> Optional[str]:
    return None

async def upsert_webhook(payload: Dict[str, Any]) -> None:
    # TODO: записать в БД (session_id, url_chunk, url_final, secret)
    return None
