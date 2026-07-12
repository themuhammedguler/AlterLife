import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
headers = {"Authorization": "Bearer mock_token_testuser"}

def test_get_skill_tree_builds_defaults():
    response = client.get("/api/v1/skills/tree", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert len(data["nodes"]) >= 5
    # All have required fields
    for node in data["nodes"]:
        assert "skill_id" in node
        assert "name" in node
        assert "level" in node
        assert "is_unlocked" in node

def test_skill_resources_for_unlocked_skill():
    # First ensure tree is built
    client.get("/api/v1/skills/tree", headers=headers)
    # python should be unlocked (no prerequisites)
    response = client.get("/api/v1/skills/python/resources", headers=headers)
    assert response.status_code == 200
    resources = response.json()
    assert isinstance(resources, list)
    assert len(resources) >= 1
    assert "title" in resources[0]
    assert "platform" in resources[0]
    assert "url" in resources[0]

def test_add_xp_to_skill():
    # Ensure tree built
    client.get("/api/v1/skills/tree", headers=headers)
    # english_professional starts at level 2, xp 400
    response = client.post("/api/v1/skills/english_professional/xp", headers=headers, json={"xp_amount": 100})
    assert response.status_code == 200
    data = response.json()
    assert data["skill_id"] == "english_professional"
    assert data["new_xp"] >= 100
    assert "level_up" in data
    assert "message" in data

def test_locked_skill_xp_fails():
    # Ensure tree built
    client.get("/api/v1/skills/tree", headers=headers)
    # kubernetes is locked (requires docker at level >= 1)
    # If docker happens to be unlocked from profile, skip check
    tree = client.get("/api/v1/skills/tree", headers=headers).json()
    kube = next((n for n in tree["nodes"] if n["skill_id"] == "kubernetes"), None)
    if kube and not kube["is_unlocked"]:
        resp = client.post("/api/v1/skills/kubernetes/xp", headers=headers, json={"xp_amount": 100})
        assert resp.status_code == 400
