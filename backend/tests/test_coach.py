from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
HEADERS = {"Authorization": "Bearer mock_token_coachuser"}


def test_coach_center_endpoints():
    generated = client.post(
        "/api/v1/simulations/generate",
        headers=HEADERS,
        json={"target": "Almanya'da Cloud Engineer olarak çalışmak"},
    )
    assert generated.status_code == 200
    sim = generated.json()

    active = client.post(
        "/api/v1/coach/active-goal",
        headers=HEADERS,
        json={"simulation_id": sim["simulation_id"], "node_id": "node_root"},
    )
    assert active.status_code == 200
    assert active.json()["node_id"] == "node_root"

    radar = client.get("/api/v1/coach/risk-radar", headers=HEADERS)
    assert radar.status_code == 200
    assert radar.json()["risks"]

    review = client.post(
        "/api/v1/coach/weekly-review",
        headers=HEADERS,
        json={"wins": ["Quest yaptım"], "blockers": ["Zaman azdı"], "energy_score": 70},
    )
    assert review.status_code == 200
    assert "next_week_focus" in review.json()

    mentor = client.post(
        "/api/v1/coach/mentor/chat",
        headers=HEADERS,
        json={"message": "Bugün ne yapmalıyım?", "tone": "playful"},
    )
    assert mentor.status_code == 200
    assert "answer" in mentor.json()

    journal = client.post(
        "/api/v1/coach/decision-journal",
        headers=HEADERS,
        json={
            "decision": "Almanya iş rotasına odaklan",
            "expectation": "3 ay içinde başvuru dosyası hazır olsun",
            "confidence": 70,
            "revisit_in_days": 30,
        },
    )
    assert journal.status_code == 200
    assert journal.json()["status"] == "open"

    listed = client.get("/api/v1/coach/decision-journal", headers=HEADERS)
    assert listed.status_code == 200
    assert listed.json()["entries"]

    timeline = client.get("/api/v1/coach/timeline", headers=HEADERS)
    assert timeline.status_code == 200
    assert len(timeline.json()["milestones"]) >= 5

    reality = client.get("/api/v1/coach/reality-check", headers=HEADERS)
    assert reality.status_code == 200
    assert "verdict" in reality.json()

    report = client.get("/api/v1/coach/report", headers=HEADERS)
    assert report.status_code == 200
    assert "AlterLife Hedef Raporu" in report.json()["markdown"]

    notifications = client.get("/api/v1/coach/notifications", headers=HEADERS)
    assert notifications.status_code == 200
    items = notifications.json()["notifications"]
    assert items

    read = client.post(
        "/api/v1/coach/notifications/read",
        headers=HEADERS,
        json={"notification_id": items[0]["notification_id"]},
    )
    assert read.status_code == 200
    assert read.json()["status"] == "read"
