from __future__ import annotations
import logging, json, sys, time

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        base = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname.lower(),
            "msg": record.getMessage(),
            "logger": record.name,
        }
        for key in ("session_id", "extra"):
            val = getattr(record, key, None)
            if val:
                base[key] = val
        return json.dumps(base, ensure_ascii=False)

def setup_json_logging(level: str = "info") -> None:
    root = logging.getLogger()
    root.handlers.clear()
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(JsonFormatter())
    root.addHandler(h)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))