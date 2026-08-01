import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
HEADERS = {"Authorization": "Bearer mock_token_agentsuser"}

AGENT_ENDPOINTS = [
    ("get", "/api/v1/agents/profile/analysis"),
    ("post", "/api/v1/agents/financial/analyze"),
    ("post", "/api/v1/agents/career/roadmap"),
    ("post", "/api/v1/agents/wellbeing/check"),
    ("post", "/api/v1/agents/migration/plan"),
    ("post", "/api/v1/agents/skills/gap"),
    ("post", "/api/v1/agents/timeline/estimate"),
]


@pytest.mark.parametrize("method,path", AGENT_ENDPOINTS)
def test_agent_endpoint_requires_authentication(method, path):
    response = getattr(client, method)(path)
    assert response.status_code == 401


@pytest.mark.parametrize("method,path", AGENT_ENDPOINTS)
def test_agent_endpoint_succeeds_for_authenticated_user(method, path):
    response = getattr(client, method)(path, headers=HEADERS)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json() != {}


def test_profile_analyzer_returns_expected_shape():
    response = client.get("/api/v1/agents/profile/analysis", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    for field in (
        "archetype",
        "archetype_description",
        "motivation_primary",
        "learning_style",
        "risk_tolerance",
        "strengths",
        "blind_spots",
        "recommended_agents",
        "motivational_message",
    ):
        assert field in data
    assert isinstance(data["strengths"], list)
    assert isinstance(data["blind_spots"], list)
    assert data["risk_tolerance"] in ("low", "medium", "high")


def test_financial_agent_returns_plan_and_savings_projection():
    response = client.post("/api/v1/agents/financial/analyze", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "monthly_plan" in data
    assert isinstance(data["monthly_plan"], list)
    assert len(data["monthly_plan"]) > 0
    assert "months_to_goal" in data
    assert "freedom_date_estimate" in data


def test_career_coach_agent_returns_roadmap_phases():
    response = client.post("/api/v1/agents/career/roadmap", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "target_role" in data
    assert "roadmap_phases" in data
    assert len(data["roadmap_phases"]) == 3
    assert all("milestones" in phase for phase in data["roadmap_phases"])


def test_wellbeing_agent_returns_burnout_assessment():
    response = client.post("/api/v1/agents/wellbeing/check", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "burnout_score" in data
    assert 0 <= data["burnout_score"] <= 100
    assert data["risk_level"] in ("Kritik", "Yüksek", "Orta", "Düşük")
    assert "recovery_recommendations" in data


def test_migration_agent_returns_country_plan():
    response = client.post("/api/v1/agents/migration/plan", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    for field in ("target_country", "visa_recommendation", "financial_estimate", "timeline", "checklist"):
        assert field in data
    assert len(data["timeline"]) == 4


def test_skill_gap_agent_returns_learning_sequence():
    response = client.post("/api/v1/agents/skills/gap", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "critical_gaps" in data
    assert "learning_sequence" in data
    assert "study_plan" in data
    assert data["study_plan"]["sessions_per_week"] > 0


def test_timeline_agent_returns_pace_comparison():
    response = client.post("/api/v1/agents/timeline/estimate", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "pace_comparison" in data
    assert len(data["pace_comparison"]) == 3
    labels = [p["label"] for p in data["pace_comparison"]]
    assert labels == ["Şu An", "Optimize", "Yoğun"]


def test_orchestrator_recommends_a_subset_of_registered_agents():
    listed = client.get("/api/v1/agents/list", headers=HEADERS)
    assert listed.status_code == 200
    all_agent_ids = set(listed.json()["agents"].keys())
    assert "financial" in all_agent_ids

    orchestrated = client.post("/api/v1/agents/orchestrate", headers=HEADERS)
    assert orchestrated.status_code == 200
    activated = set(orchestrated.json().get("agent_descriptions", {}).keys())
    assert activated.issubset(all_agent_ids)
