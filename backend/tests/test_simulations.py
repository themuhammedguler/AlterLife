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


def test_branch_action_plan_includes_resources_and_shared_code():
    headers = {"Authorization": "Bearer mock_token_testuser"}
    response = client.post(
        "/api/v1/simulations/sim_usr_testuser/nodes/node_root/action-plan",
        headers=headers,
        json={"friend_code": "BERLIN42"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["node_id"] == "node_root"
    assert data["realism_score"] >= 35
    assert len(data["steps"]) >= 4
    assert len(data["resources"]) >= 3
    assert data["shared_path"]["code"]
    assert data["shared_path"]["divergence_options"]
    assert data["done_so_far"]


def test_branch_action_plan_is_private_to_owner():
    attacker_headers = {"Authorization": "Bearer mock_token_attacker"}
    response = client.post(
        "/api/v1/simulations/sim_usr_testuser/nodes/node_root/action-plan",
        headers=attacker_headers,
        json={},
    )
    assert response.status_code == 403


def test_simulation_is_private_to_owner():
    attacker_headers = {"Authorization": "Bearer mock_token_attacker"}
    attempts = (
        ("get", "/api/v1/simulations/sim_usr_testuser/tree", None),
        (
            "post",
            "/api/v1/simulations/sim_usr_testuser/branch",
            {"parent_node_id": "node_root", "decision_text": "Yetkisiz dal denemesi"},
        ),
        ("post", "/api/v1/simulations/sim_usr_testuser/stress-test?node_id=node_root", None),
    )
    for method, path, payload in attempts:
        request = getattr(client, method)
        response = request(path, headers=attacker_headers, **({"json": payload} if payload else {}))
        assert response.status_code == 403


def test_simulation_input_limits():
    headers = {"Authorization": "Bearer mock_token_testuser"}
    response = client.post("/api/v1/simulations/generate", headers=headers, json={"target": "x"})
    assert response.status_code == 422
