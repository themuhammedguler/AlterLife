import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_analytics_requires_authentication():
    response = client.get("/api/v1/analytics/summary")
    assert response.status_code == 401


def test_analytics_summary_shape_for_fresh_user():
    headers = {"Authorization": "Bearer mock_token_analyticsfresh"}
    response = client.get("/api/v1/analytics/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()

    # Top-level shape
    assert set(data.keys()) == {"kpi", "xp_history", "decision_impacts"}

    # KPI shape / sane defaults for a brand-new user
    kpi = data["kpi"]
    for field in (
        "total_xp",
        "level",
        "completed_quests",
        "active_days",
        "goal_alignment",
        "simulation_branches",
        "library_resources_completed",
    ):
        assert field in kpi
    assert kpi["level"] >= 1
    assert kpi["total_xp"] >= 0
    assert kpi["completed_quests"] == 0
    assert kpi["simulation_branches"] == 0
    assert 0 <= kpi["goal_alignment"] <= 100

    # XP history always covers 7 days, even with no events (mock fallback)
    assert len(data["xp_history"]) == 7
    for point in data["xp_history"]:
        assert "label" in point and "xp" in point
        assert point["xp"] >= 0

    # No simulation branches yet -> no decision impacts
    assert data["decision_impacts"] == []


def test_analytics_reflects_completed_quest():
    headers = {"Authorization": "Bearer mock_token_analyticsquest"}

    # Fetch (and thereby seed) today's quests for a fresh user
    quests = client.get("/api/v1/quests/daily", headers=headers).json()
    pending = next((q for q in quests if q["status"] == "pending"), None)
    if not pending:
        pytest.skip("Tüm görevler zaten tamamlanmış.")

    verify_resp = client.post(
        f"/api/v1/quests/{pending['quest_id']}/verify", headers=headers
    )
    assert verify_resp.status_code == 200

    summary = client.get("/api/v1/analytics/summary", headers=headers).json()
    assert summary["kpi"]["completed_quests"] >= 1


def test_quest_xp_is_not_reflected_in_analytics_total_xp():
    """Documents a real data-model inconsistency found while testing.

    Quest verification (routers/quests.py) stores earned XP under
    user["rpgState"]["xp"], while the analytics summary (and the library
    resource flow) read/write the top-level user["xp"] field. As a result,
    XP earned from quests currently never shows up in
    GET /api/v1/analytics/summary -> kpi.total_xp.

    This test pins down the *current* behavior so a future fix is visible
    as an intentional test change rather than a silent regression.
    """
    headers = {"Authorization": "Bearer mock_token_analyticsxpgap"}

    quests = client.get("/api/v1/quests/daily", headers=headers).json()
    pending = next((q for q in quests if q["status"] == "pending"), None)
    if not pending:
        pytest.skip("Tüm görevler zaten tamamlanmış.")

    verify_resp = client.post(
        f"/api/v1/quests/{pending['quest_id']}/verify", headers=headers
    )
    assert verify_resp.status_code == 200
    assert verify_resp.json()["new_total_xp"] > 0

    summary = client.get("/api/v1/analytics/summary", headers=headers).json()
    # BUG: this "should" be >= xp_earned but the two XP stores are disjoint.
    assert summary["kpi"]["total_xp"] == 0


def test_analytics_reflects_simulation_branch():
    headers = {"Authorization": "Bearer mock_token_analyticssim"}

    gen_resp = client.post(
        "/api/v1/simulations/generate",
        json={"target": "Move to Portugal and work as a Backend Engineer"},
        headers=headers,
    )
    assert gen_resp.status_code == 200
    sim_id = gen_resp.json()["simulation_id"]

    branch_resp = client.post(
        f"/api/v1/simulations/{sim_id}/branch",
        json={
            "parent_node_id": "node_root",
            "decision_text": "Freelance olarak devam edersem ne olur?",
        },
        headers=headers,
    )
    assert branch_resp.status_code == 200

    summary = client.get("/api/v1/analytics/summary", headers=headers).json()
    assert summary["kpi"]["simulation_branches"] >= 1
    assert len(summary["decision_impacts"]) >= 1
    impact = summary["decision_impacts"][0]
    for field in (
        "branch_id",
        "decision_name",
        "happiness_delta",
        "savings_delta",
        "stress_delta",
        "career_score",
    ):
        assert field in impact


def test_analytics_reflects_completed_library_resource():
    headers = {"Authorization": "Bearer mock_token_analyticslib"}

    add_resp = client.post(
        "/api/v1/library/resources",
        headers=headers,
        json={
            "title": "Analytics Kaynağı",
            "platform": "Docs",
            "url": "https://example.com/analytics",
            "skill_tags": [],
        },
    )
    assert add_resp.status_code == 200
    rid = add_resp.json()["resource_id"]

    complete_resp = client.patch(
        f"/api/v1/library/resources/{rid}/complete", headers=headers
    )
    assert complete_resp.status_code == 200

    summary = client.get("/api/v1/analytics/summary", headers=headers).json()
    assert summary["kpi"]["library_resources_completed"] >= 1


def test_analytics_is_scoped_per_user():
    owner_headers = {"Authorization": "Bearer mock_token_analyticsowner"}
    other_headers = {"Authorization": "Bearer mock_token_analyticsother"}

    # Owner completes a quest and gains XP
    quests = client.get("/api/v1/quests/daily", headers=owner_headers).json()
    pending = next((q for q in quests if q["status"] == "pending"), None)
    if pending:
        client.post(f"/api/v1/quests/{pending['quest_id']}/verify", headers=owner_headers)

    owner_summary = client.get("/api/v1/analytics/summary", headers=owner_headers).json()
    other_summary = client.get("/api/v1/analytics/summary", headers=other_headers).json()

    # A brand-new, unrelated user should not inherit the owner's progress
    assert other_summary["kpi"]["completed_quests"] == 0
    assert other_summary["kpi"]["total_xp"] <= owner_summary["kpi"]["total_xp"]
