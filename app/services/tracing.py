import json, time, sys
def log_event(event: str, service: str = "module2", session_id=None, seq=None, status="ok", latency_ms=None, **extra):
    rec = {
        "ts": int(time.time()*1000),
        "service": service,
        "event": event,
        "session_id": session_id,
        "seq": seq,
        "status": status,
        "latency_ms": latency_ms,
    }
    rec.update(extra or {})
    print(json.dumps(rec, ensure_ascii=False), file=sys.stdout, flush=True)
