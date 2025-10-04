import json

def sse_event(event: str, data: dict) -> str:
    """
    Формирует строку SSE-события.
    """
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
