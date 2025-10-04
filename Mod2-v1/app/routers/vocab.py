from pathlib import Path
import json
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.models.schemas import VocabSchema

router = APIRouter(prefix="/v2/vocab", tags=["vocab"])

# Абсолютный путь к /config/vocab.json относительно корня проекта
BASE_DIR = Path(__file__).resolve().parents[2]
VOCAB_PATH = BASE_DIR / "config" / "vocab.json"


def _default_vocab() -> dict:
    return {
        "vocab_version": "0.1.0",
        "terms": [
            {"lemma": "кнопка", "aliases": ["button", "btn"], "element": "ui.button"},
            {"lemma": "форма", "aliases": ["формочка", "form"], "element": "ui.form"},
        ],
    }


@router.get("")
def get_vocab():
    if not VOCAB_PATH.exists():
        # если файла нет — отдаем заглушку (критерий: заглушка отдается)
        return JSONResponse(content=_default_vocab(), status_code=200)
    try:
        data = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
        return JSONResponse(content=data, status_code=200)
    except Exception as e:
        # читаемая ошибка при проблемах чтения файла
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to read vocab.json: {e}"},
        )


@router.post("/sync")
def sync_vocab(vocab: VocabSchema):
    # Валидация схемы происходит через Pydantic (критерий: валидация входов)
    try:
        VOCAB_PATH.parent.mkdir(parents=True, exist_ok=True)
        VOCAB_PATH.write_text(json.dumps(vocab.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
        return {"status": "ok"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to write vocab.json: {e}"},
        )
