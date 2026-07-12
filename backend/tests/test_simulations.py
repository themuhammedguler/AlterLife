import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_generate_simulation():
    # Call generate with mock token to auto-create profile
    headers = {"Authorization": "Bearer mock_token_testuser"}
    response = client.post(
        "/api/v1/simulations/generate",
        json={"target": "Move to Germany and work as a Cloud Engineer"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "simulation_id" in data
    assert "nodes" in data
    assert len(data["nodes"]) >= 2
    assert data["nodes"][0]["decision_name"] == "Başlangıç Durumu"

def test_branch_simulation():
    headers = {"Authorization": "Bearer mock_token_testuser"}
    # Generate tree first
    response = client.post(
        "/api/v1/simulations/generate",
        json={"target": "Move to Germany and work as a Cloud Engineer"},
        headers=headers
    )
    sim_id = response.json()["simulation_id"]

    # Create a branch from node_root
    branch_response = client.post(
        f"/api/v1/simulations/{sim_id}/branch",
        json={
            "parent_node_id": "node_root",
            "decision_text": "Aşık olup kariyeri yavaşlatırsam ne olur?"
        },
        headers=headers
    )
    assert branch_response.status_code == 200
    branch_data = branch_response.json()
    assert branch_data["parent"] == "node_root"
    assert "metrics" in branch_data
    assert len(branch_data["milestones"]) > 0

def test_get_simulation_tree():
    headers = {"Authorization": "Bearer mock_token_testuser"}
    response = client.get(
        "/api/v1/simulations/sim_usr_testuser/tree",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["simulation_id"] == "sim_usr_testuser"
    assert len(data["nodes"]) >= 2

def test_stress_test():
    headers = {"Authorization": "Bearer mock_token_testuser"}
    # Call stress test on node_root
    response = client.post(
        "/api/v1/simulations/sim_usr_testuser/stress-test?node_id=node_root",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["parent"] == "node_root"
    assert "metrics" in data
    assert len(data["milestones"]) > 0
