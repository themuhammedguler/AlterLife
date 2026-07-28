from api.v1.services import avatar_service


def test_avatar_passes_photo_mime_type_to_groq(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    captured = {}

    def fake_analyze(photo_base64, prompt, mime_type):
        captured["mime_type"] = mime_type
        return "dark hair, glasses"

    monkeypatch.setattr(avatar_service, "analyze_image_with_groq", fake_analyze)
    result = avatar_service.generate_avatar(
        "usr_test",
        photo_base64="ZmFrZQ==",
        photo_mime_type="image/png",
    )

    assert captured["mime_type"] == "image/png"
    assert result["avatar_type"] == "dicebear"


def test_real_image_provider_overrides_dicebear(monkeypatch):
    monkeypatch.setattr(avatar_service, "generate_ai_image", lambda prompt: "https://example.com/avatar.png")

    result = avatar_service.generate_avatar("usr_test", description="neon explorer")

    assert result["avatar_type"] == "ai_generated"
    assert result["avatar_url"] == "https://example.com/avatar.png"
