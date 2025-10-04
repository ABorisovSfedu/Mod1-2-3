import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_batch_transcribe_stub():
    fake = io.BytesIO(b"webm data")
    files = { "file": ("test.webm", fake, "audio/webm") }
    r = client.post("/v1/transcribe?session_id=it1&lang=ru-RU", files=files)
    assert r.status_code == 200
    data = r.json()
    assert data["session_id"] == "it1"
    assert "text_full" in data and len(data["text_full"]) > 0
    assert len(data["chunks"]) >= 1
    seqs = [c["seq"] for c in data["chunks"]]
    assert seqs == sorted(seqs)