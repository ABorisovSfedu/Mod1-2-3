from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_chunk_then_layout():
    # отправляем чанк
    r = client.post("/v2/ingest/chunk", json={
        "session_id": "sess1",
        "chunk_id": "c1",
        "seq": 0,
        "text": "Нужна форма обратной связи и каталог услуг",
        "lang": "ru"
    })
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert any(m["element"] == "ContactForm" for m in data["mappings"])
    assert any(m["element"] == "ServicesGrid" for m in data["mappings"])

    # читаем layout
    r2 = client.get("/v2/session/sess1/layout")
    assert r2.status_code == 200
    layout = r2.json()["layout"]
    assert layout["template"] == "hero-main-footer"
    # компоненты должны попасть в секции по правилам
    sections = layout["sections"]
    main_names = [c["component"] for c in sections["main"]]
    footer_names = [c["component"] for c in sections["footer"]]
    assert "ServicesGrid" in main_names
    assert "ContactForm" in footer_names
