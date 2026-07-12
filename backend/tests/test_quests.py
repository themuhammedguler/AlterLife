import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_daily_quests_retrieval():
    headers = {"Authorization": "Bearer mock_token_testuser"}
    response = client.get(
        "/api/v1/quests/daily",
        headers=headers
    )
    assert response.status_code == 200
    quests = response.json()
    assert len(quests) == 3
    assert quests[0]["quest_id"] == "qst_theory"
    assert quests[1]["quest_id"] == "qst_practice"
    assert quests[2]["quest_id"] == "qst_general"

def test_verify_quest():
    headers = {"Authorization": "Bearer mock_token_testuser2"}

    # Retrieve quests first to initialize them (fresh user)
    quests_resp = client.get("/api/v1/quests/daily", headers=headers)
    assert quests_resp.status_code == 200
    quests = quests_resp.json()

    # Find a pending quest
    pending = next((q for q in quests if q["status"] == "pending"), None)
    if not pending:
        pytest.skip("Tüm görevler zaten tamamlanmış.")

    # Verify the pending quest
    response = client.post(
        f"/api/v1/quests/{pending['quest_id']}/verify",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quest_id"] == pending["quest_id"]
    assert data["status"] == "completed"
    assert data["xp_earned"] >= 0
    assert "new_total_xp" in data
    assert "level_up" in data

