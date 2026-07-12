import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
headers = {"Authorization": "Bearer mock_token_testuser"}

def test_list_library_seeds_defaults():
    # Fresh call should return seeded resources
    response = client.get("/api/v1/library/resources", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "resource_id" in data[0]
    assert "title" in data[0]

def test_add_resource():
    response = client.post("/api/v1/library/resources", headers=headers, json={
        "title": "Test Resource",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=test",
        "skill_tags": ["Test", "QA"],
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Resource"
    assert data["is_completed"] is False
    assert data["xp_reward"] == 50

def test_complete_resource():
    # Add first to ensure we have a resource
    add_resp = client.post("/api/v1/library/resources", headers=headers, json={
        "title": "Complete Me",
        "platform": "Docs",
        "url": "https://example.com",
        "skill_tags": [],
    })
    assert add_resp.status_code == 200
    rid = add_resp.json()["resource_id"]

    # Complete it
    resp = client.patch(f"/api/v1/library/resources/{rid}/complete", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_completed"] is True
    assert data["xp_earned"] == 50

    # Try to complete again – should fail
    resp2 = client.patch(f"/api/v1/library/resources/{rid}/complete", headers=headers)
    assert resp2.status_code == 400

def test_delete_resource():
    # Add a resource to delete
    add_resp = client.post("/api/v1/library/resources", headers=headers, json={
        "title": "Delete Me",
        "platform": "Article",
        "url": "https://delete-me.com",
        "skill_tags": [],
    })
    rid = add_resp.json()["resource_id"]

    # Delete it
    resp = client.delete(f"/api/v1/library/resources/{rid}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True

    # Verify deleted
    resources = client.get("/api/v1/library/resources", headers=headers).json()
    ids = [r["resource_id"] for r in resources]
    assert rid not in ids
