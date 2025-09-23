from app.services.sse import sse_event

def test_sse_event_format():
    evt = sse_event("preview", {"x": 1})
    assert evt.startswith("event: preview\n")
    assert "data: " in evt
    assert evt.endswith("\n\n")
