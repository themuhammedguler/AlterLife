import pytest

from api.v1.services import ai_service


class _FakeResponse:
    def __init__(self, content: str):
        self._content = content

    def raise_for_status(self):
        return None

    def json(self):
        return {"choices": [{"message": {"content": self._content}}]}


def test_call_groq_json_object(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(
        ai_service.httpx,
        "post",
        lambda *args, **kwargs: _FakeResponse('{"status":"ok"}'),
    )

    assert ai_service.call_groq_json("JSON döndür") == {"status": "ok"}


def test_call_groq_json_unwraps_array(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(
        ai_service.httpx,
        "post",
        lambda *args, **kwargs: _FakeResponse('{"items":[{"title":"Kaynak"}]}'),
    )

    assert ai_service.call_groq_json("Kaynakları döndür", expect_array=True) == [
        {"title": "Kaynak"}
    ]


def test_call_groq_json_uses_fallback_when_key_missing(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(ai_service.AIProviderUnavailable):
        ai_service.call_groq_json("JSON döndür")


def test_analyze_image_uses_configured_vision_model(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("GROQ_VISION_MODEL", "vision-test")
    captured = {}

    def fake_post(*args, **kwargs):
        captured.update(kwargs["json"])
        return _FakeResponse("fotoğraf açıklaması")

    monkeypatch.setattr(ai_service.httpx, "post", fake_post)

    result = ai_service.analyze_image_with_groq("ZmFrZQ==", "Fotoğrafı analiz et")

    assert result == "fotoğraf açıklaması"
    assert captured["model"] == "vision-test"
    image_url = captured["messages"][0]["content"][1]["image_url"]["url"]
    assert image_url == "data:image/jpeg;base64,ZmFrZQ=="


def test_call_groq_json_retries_missing_required_fields(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    responses = iter([_FakeResponse('{"name":"first"}'), _FakeResponse('{"name":"second","score":90}')])
    monkeypatch.setattr(ai_service.httpx, "post", lambda *args, **kwargs: next(responses))

    result = ai_service.call_groq_json(
        "JSON döndür",
        required_keys=("name", "score"),
        retries=1,
    )

    assert result == {"name": "second", "score": 90}


def test_research_uses_compound_model(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    captured = {}

    def fake_post(*args, **kwargs):
        captured.update(kwargs["json"])
        return _FakeResponse('{"result":"verified"}')

    monkeypatch.setattr(ai_service.httpx, "post", fake_post)

    assert ai_service.call_groq_research_json("Araştır") == {"result": "verified"}
    assert captured["model"] == "groq/compound"
    assert "response_format" not in captured
