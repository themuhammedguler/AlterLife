import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_training_pipeline_mock():
    """
    Test the agent training pipeline with mocked LLM calls
    (it will fall back to heuristic mocks).
    """
    headers = {"Authorization": "Bearer mock_token_testuser"}
    response = client.post(
        "/api/v1/agents/train",
        headers=headers,
        json={
            "scenario_ids": ["sc_001", "sc_003"],
            "agents_to_test": ["migration", "timeline"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "pipeline_run_summary" in data
    assert "agent_performance" in data
    assert "scenario_results" in data
    
    summary = data["pipeline_run_summary"]
    assert summary["scenarios_tested"] == 2
    assert summary["agents_tested"] == 2
    
    performance = data["agent_performance"]
    assert "migration" in performance
    assert "timeline" in performance
    
    # Check that they received grades
    assert "grade" in performance["migration"]
    assert "grade" in performance["timeline"]

def test_orchestrator():
    """
    Test the central brain orchestrator endpoint.
    """
    headers = {"Authorization": "Bearer mock_token_testuser"}
    response = client.post("/api/v1/agents/orchestrate", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert "user_archetype" in data
    assert "unified_report" in data
    assert "today_focus" in data["unified_report"]
    assert "agent_results" in data
    
    # Based on the test profile, some agents should be activated
    assert "activated_agents" in data
    assert isinstance(data["activated_agents"], list)

def test_list_agents():
    """
    Test listing all registered agents.
    """
    response = client.get("/api/v1/agents/list")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert "financial" in data["agents"]
    assert "career_coach" in data["agents"]
