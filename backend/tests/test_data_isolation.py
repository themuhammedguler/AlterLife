"""
Data-isolation tests.

These pin down that one user's token can never read or mutate another
user's resources across the routers that store per-user state (library,
skills, coach active-goal). Several of these already behave correctly by
construction (resources are looked up from that user's own storage
bucket), but nothing previously asserted this in a test, so a future
refactor (e.g. moving to a shared/global resource table) could silently
introduce a leak without failing the suite.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

OWNER = {"Authorization": "Bearer mock_token_isoowner"}
ATTACKER = {"Authorization": "Bearer mock_token_isoattacker"}


def test_coach_rejects_setting_active_goal_on_someone_elses_simulation():
    # Owner generates their own simulation tree.
    gen = client.post(
        "/api/v1/simulations/generate",
        headers=OWNER,
        json={"target": "Berlin'de Cloud Engineer olmak"},
    )
    assert gen.status_code == 200
    owner_sim_id = gen.json()["simulation_id"]

    # Attacker tries to set their active goal against the owner's simulation id.
    response = client.post(
        "/api/v1/coach/active-goal",
        headers=ATTACKER,
        json={"simulation_id": owner_sim_id, "node_id": "node_root"},
    )
    assert response.status_code == 403


def test_coach_active_goal_accepts_users_own_simulation():
    gen = client.post(
        "/api/v1/simulations/generate",
        headers=ATTACKER,
        json={"target": "Lizbon'da Backend Engineer olmak"},
    )
    own_sim_id = gen.json()["simulation_id"]

    response = client.post(
        "/api/v1/coach/active-goal",
        headers=ATTACKER,
        json={"simulation_id": own_sim_id, "node_id": "node_root"},
    )
    assert response.status_code == 200


def test_library_resource_is_not_visible_or_mutable_by_other_users():
    add_resp = client.post(
        "/api/v1/library/resources",
        headers=OWNER,
        json={
            "title": "Sadece Owner'a Ait",
            "platform": "Docs",
            "url": "https://example.com/owner-only",
            "skill_tags": [],
        },
    )
    assert add_resp.status_code == 200
    resource_id = add_resp.json()["resource_id"]

    # The attacker's own library listing must not contain the owner's resource.
    attacker_library = client.get("/api/v1/library/resources", headers=ATTACKER).json()
    attacker_ids = [r["resource_id"] for r in attacker_library]
    assert resource_id not in attacker_ids

    # The attacker cannot complete or delete a resource_id that only exists
    # in the owner's library.
    complete_resp = client.patch(
        f"/api/v1/library/resources/{resource_id}/complete", headers=ATTACKER
    )
    assert complete_resp.status_code == 404

    delete_resp = client.delete(
        f"/api/v1/library/resources/{resource_id}", headers=ATTACKER
    )
    assert delete_resp.status_code == 404

    # The owner can still complete their own resource afterwards.
    owner_complete = client.patch(
        f"/api/v1/library/resources/{resource_id}/complete", headers=OWNER
    )
    assert owner_complete.status_code == 200


def test_custom_skill_is_not_mutable_by_other_users():
    add_resp = client.post(
        "/api/v1/skills/custom",
        headers=OWNER,
        json={"name": "Owner'a Özel Beceri", "category": "Backend"},
    )
    assert add_resp.status_code == 200
    skill_id = add_resp.json()["skill_id"]

    # Attacker cannot reposition or delete a skill node that lives only in
    # the owner's skill tree.
    reposition_resp = client.patch(
        f"/api/v1/skills/{skill_id}/position",
        headers=ATTACKER,
        json={"canvas_x": 10, "canvas_y": 10},
    )
    assert reposition_resp.status_code == 404

    delete_resp = client.delete(f"/api/v1/skills/{skill_id}/custom", headers=ATTACKER)
    assert delete_resp.status_code == 404

    # Owner can still manage their own custom skill.
    owner_reposition = client.patch(
        f"/api/v1/skills/{skill_id}/position",
        headers=OWNER,
        json={"canvas_x": 42, "canvas_y": 42},
    )
    assert owner_reposition.status_code == 200


def test_community_memberships_are_scoped_per_user():
    paths = client.get("/api/v1/community/paths", headers=OWNER).json()["paths"]
    if not paths:
        pytest.skip("Topluluk rotası bulunamadı.")
    path_id = paths[0]["id"] if "id" in paths[0] else paths[0].get("path_id")
    if not path_id:
        pytest.skip("Rota kimliği bulunamadı.")

    join_resp = client.post(
        f"/api/v1/community/paths/{path_id}/join", headers=OWNER, json={}
    )
    assert join_resp.status_code == 200

    owner_memberships = client.get("/api/v1/community/me/paths", headers=OWNER).json()
    attacker_memberships = client.get(
        "/api/v1/community/me/paths", headers=ATTACKER
    ).json()

    assert len(owner_memberships["memberships"]) >= 1
    owner_path_ids = {m.get("path_id") for m in owner_memberships["memberships"]}
    attacker_path_ids = {m.get("path_id") for m in attacker_memberships["memberships"]}
    assert path_id in owner_path_ids
    assert path_id not in attacker_path_ids
