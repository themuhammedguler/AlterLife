"""
Test: Community RAG & Briefing yeni endpoint'leri
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
HEADERS = {"Authorization": "Bearer mock_token_testuser_new"}


# ── Community Endpoints ───────────────────────────────────────────────────────

def test_community_paths_list():
    """GET /community/paths topluluk yollarını listeler."""
    resp = client.get("/api/v1/community/paths?limit=5", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "paths" in data
    assert isinstance(data["paths"], list)
    assert data["total"] > 0


def test_community_search_rag():
    """POST /community/paths/search RAG ile arama yapar."""
    resp = client.post(
        "/api/v1/community/paths/search",
        json={"goal": "Almanya'da yazılım mühendisi", "top_k": 3},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "paths" in data
    assert "query" in data
    assert isinstance(data["paths"], list)


def test_community_search_empty_returns_empty():
    """Boş arama sorgusu boş liste döner."""
    resp = client.post(
        "/api/v1/community/paths/search",
        json={"goal": "", "top_k": 3},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["paths"] == []


def test_community_share_path():
    """POST /community/share yeni yol paylaşır."""
    resp = client.post(
        "/api/v1/community/share",
        json={
            "goal": "Test hedefi",
            "steps": ["Adım 1", "Adım 2"],
            "outcome": "Test sonucu",
            "tags": ["test"]
        },
        headers=HEADERS,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "path_id" in data


def test_community_stats():
    """GET /community/stats istatistik döner."""
    resp = client.get("/api/v1/community/stats", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_paths" in data
    assert "success_rate" in data
    assert "avg_duration_months" in data


# ── Briefing Endpoints ────────────────────────────────────────────────────────

def test_daily_briefing_text():
    """GET /briefing/daily günlük brifing metni döner."""
    resp = client.get("/api/v1/briefing/daily", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "text" in data
    assert len(data["text"]) > 20  # Non-empty text
    assert "tts_engine" in data
    assert "audio_available" in data


def test_tts_status():
    """GET /briefing/tts/status TTS motor durumu döner."""
    resp = client.get("/api/v1/briefing/tts/status", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "gtts" in data
    assert "active_engine" in data


def test_tts_synthesis():
    """POST /briefing/tts metin→ses çevirimi yapar (veya None döner, hata atmaz)."""
    resp = client.post(
        "/api/v1/briefing/tts",
        json={"text": "Merhaba, bu bir test mesajıdır.", "lang": "tr"},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    data = resp.json()
    # audio_base64 None olabilir (gTTS internete erişemezse), ama 200 dönmeli
    assert "audio_available" in data


# ── RPG Energy/Focus & Rest ───────────────────────────────────────────────────

def test_profile_has_energy_focus():
    """GET /user/profile energy ve focus alanlarını döner."""
    resp = client.get("/api/v1/user/profile", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "energy" in data
    assert "focus" in data
    assert "max_energy" in data
    assert "max_focus" in data
    assert data["energy"] >= 0
    assert data["max_energy"] >= 1


def test_user_rest_endpoint():
    """POST /user/rest energy ve focus'u yeniler."""
    resp = client.post("/api/v1/user/rest", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["energy"] == 100
    assert data["focus"] == 100
    assert data["xp_gained"] == 25


# ── Custom Skill Endpoints ────────────────────────────────────────────────────

def test_add_custom_skill():
    """POST /skills/custom özel yetenek ekler."""
    resp = client.post(
        "/api/v1/skills/custom",
        json={"name": "TestKotlin", "category": "Backend", "description": "Kotlin programlama dili"},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "skill_id" in data
    assert data["skill_id"].startswith("custom_")
    return data["skill_id"]


def test_update_skill_position():
    """PATCH /skills/{id}/position canvas koordinatını kaydeder."""
    # Önce özel yetenek ekle
    add_resp = client.post(
        "/api/v1/skills/custom",
        json={"name": "PosTestSkill", "category": "Cloud"},
        headers=HEADERS,
    )
    skill_id = add_resp.json()["skill_id"]

    resp = client.patch(
        f"/api/v1/skills/{skill_id}/position",
        json={"canvas_x": 150.0, "canvas_y": 200.0},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["canvas_x"] == 150.0


def test_delete_custom_skill():
    """DELETE /skills/{id}/custom özel yeteneği siler."""
    # Önce ekle
    add_resp = client.post(
        "/api/v1/skills/custom",
        json={"name": "DeleteMeSkill", "category": "Custom"},
        headers=HEADERS,
    )
    skill_id = add_resp.json()["skill_id"]

    # Sil
    del_resp = client.delete(f"/api/v1/skills/{skill_id}/custom", headers=HEADERS)
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "success"


def test_delete_system_skill_forbidden():
    """Sistem yeteneğini silmeye çalışmak 403 döner."""
    # python skill_id'si sistem yeteneklerinden biridir
    resp = client.delete("/api/v1/skills/python/custom", headers=HEADERS)
    # 403 veya 404 bekleniyor (python custom değil, ya bulunamaz ya da forbidden)
    assert resp.status_code in (403, 404)
