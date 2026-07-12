import pytest
from fastapi.testclient import TestClient
from main import app
from api.v1.database import save_daily_quests, save_user

client = TestClient(app)

def test_google_calendar_connect():
    headers = {"Authorization": "Bearer mock_token_testuser_sync"}
    
    # 1. Connect Google Calendar with mock code
    response = client.post(
        "/api/v1/integrations/calendar/connect",
        json={"code": "mock_code_calendar", "redirect_uri": "http://localhost:3000/callback"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "connected"
    
    # 2. Verify status is connected
    res_status = client.get("/api/v1/integrations/calendar/status", headers=headers)
    assert res_status.status_code == 200
    assert res_status.json()["is_connected"] is True
    assert res_status.json()["username"] == "mock_google_user@gmail.com"

def test_github_connect():
    headers = {"Authorization": "Bearer mock_token_testuser_sync"}
    
    # 1. Connect GitHub with mock code
    response = client.post(
        "/api/v1/integrations/github/connect",
        json={"code": "mock_code_github", "redirect_uri": "http://localhost:3000/callback"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "connected"
    
    # 2. Verify status
    res_status = client.get("/api/v1/integrations/github/status", headers=headers)
    assert res_status.status_code == 200
    assert res_status.json()["is_connected"] is True
    assert res_status.json()["username"] == "mock_github_user"

def test_quest_sync_verification():
    headers = {"Authorization": "Bearer mock_token_testuser_sync"}
    
    # 1. Setup mock calendar and github connections
    user_id = "usr_testuser_sync"
    user_data = {
        "userId": user_id,
        "email": "test_sync@alterlife.io",
        "integrations": {
            "google_calendar": {
                "access_token": "mock_access_token",
                "connected_at": "2026-07-09T00:00:00Z"
            },
            "github": {
                "access_token": "mock_github_access_token",
                "username": "mock_github_user"
            }
        }
    }
    save_user(user_id, user_data)
    
    # 2. Save a pending quest that requires github_commit and calendar_sync
    quests = [
        {
            "quest_id": "quest_sync_1",
            "title": "Study Cloud Networking",
            "description": "20 minutes study",
            "xp_reward": 100,
            "status": "pending",
            "verified_by": "calendar_sync"
        },
        {
            "quest_id": "quest_sync_2",
            "title": "Commit dockerfile change",
            "description": "Git commit",
            "xp_reward": 150,
            "status": "pending",
            "verified_by": "github_commit"
        }
    ]
    save_daily_quests(user_id, quests)
    
    # 3. Request daily quests (this should trigger sync_and_verify_quests)
    response = client.get("/api/v1/quests/daily", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    # Verify that they were marked completed by the mock sync checker
    assert data[0]["status"] == "completed"
    assert data[1]["status"] == "completed"
