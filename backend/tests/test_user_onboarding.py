from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_onboarding_requires_authentication():
    response = client.post("/api/v1/user/onboarding", json={"field": "software"})
    assert response.status_code == 401


def test_onboarding_creates_profile_rpg_state_and_simulation():
    headers = {"Authorization": "Bearer mock_token_onboarduser"}
    response = client.post(
        "/api/v1/user/onboarding",
        headers=headers,
        json={
            "status": "seeking",
            "age": "27",
            "city": "İzmir, Türkiye",
            "field": "software",
            "workPrefs": ["remote"],
            "freeGoal": "2 yıl içinde yurt dışında çalışmak",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["user_id"] == "usr_onboarduser"
    assert data["simulation_id"] == "sim_usr_onboarduser"
    assert data["avatar_url"]

    # Onboarding should have normalized the shorthand "software" field into a
    # readable role and started the RPG state.
    profile = client.get("/api/v1/user/profile", headers=headers).json()
    assert profile["role"] == "Software Developer"
    assert profile["level"] == 1
    assert profile["xp"] == 100
    assert profile["avatar_url"]

    # And it should have auto-generated an initial decision tree for the goal.
    tree = client.get(
        f"/api/v1/simulations/sim_usr_onboarduser/tree", headers=headers
    )
    assert tree.status_code == 200
    assert len(tree.json()["nodes"]) >= 2


def test_onboarding_normalizes_shorthand_roles():
    cases = {
        "design": "UI/UX Designer",
        "finance": "Financial Analyst",
        "startup": "Startup Founder",
    }
    for idx, (shorthand, expected_role) in enumerate(cases.items()):
        headers = {"Authorization": f"Bearer mock_token_roleuser{idx}"}
        response = client.post(
            "/api/v1/user/onboarding", headers=headers, json={"field": shorthand}
        )
        assert response.status_code == 200
        profile = client.get("/api/v1/user/profile", headers=headers).json()
        assert profile["role"] == expected_role


def test_onboarding_defaults_when_no_role_or_field_given():
    headers = {"Authorization": "Bearer mock_token_defaultroleuser"}
    response = client.post("/api/v1/user/onboarding", headers=headers, json={})
    assert response.status_code == 200
    profile = client.get("/api/v1/user/profile", headers=headers).json()
    assert profile["role"] == "Software Developer"


def test_avatar_generate_requires_authentication():
    response = client.post("/api/v1/user/avatar/generate", json={"description": "a hero"})
    assert response.status_code == 401


def test_avatar_generate_before_any_profile_exists_breaks_get_profile():
    """Documents a real crash bug found while testing.

    UserDoc.displayName defaults to None (api/v1/models.py). save_user()
    always round-trips data through UserDoc(**merged).model_dump(), so any
    write that doesn't include displayName persists it as an *explicit*
    None rather than omitting the key. routers/user.py's generate_avatar
    does exactly that when called for a user who has never hit /profile or
    /onboarding first: it saves {"profile": {"avatarUrl": ...}} with no
    displayName.

    The next GET /user/profile call sees a truthy user_data dict (so it
    skips its own default-seeding branch) and does
    user_data.get("displayName", "Test Kullanıcı") — which returns None,
    not the fallback, because the key is present. UserProfileResponse
    requires display_name: str, so the request 500s.

    This test pins the current (broken) behavior so a fix is visible as an
    intentional test change rather than a silent regression.
    """
    headers = {"Authorization": "Bearer mock_token_avatarfirstuser"}

    avatar_resp = client.post(
        "/api/v1/user/avatar/generate",
        headers=headers,
        json={"description": "Solo explorer, no prior profile"},
    )
    assert avatar_resp.status_code == 200

    # BUG: this should be 200, but the corrupted displayName=None crashes
    # response validation, surfacing as a 500 to a real HTTP client.
    from starlette.testclient import TestClient as _TestClient

    no_raise_client = _TestClient(app, raise_server_exceptions=False)
    profile_resp = no_raise_client.get("/api/v1/user/profile", headers=headers)
    assert profile_resp.status_code == 500


def test_avatar_generate_works_when_profile_already_exists():
    # Workaround / non-buggy path: seed the profile first (as onboarding or
    # a prior GET /profile call would), then avatar generation should not
    # corrupt it.
    headers = {"Authorization": "Bearer mock_token_avataruser"}
    client.get("/api/v1/user/profile", headers=headers)

    response = client.post(
        "/api/v1/user/avatar/generate",
        headers=headers,
        json={"description": "Futuristic explorer with a blue cape"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["avatar_url"]
    assert "avatar_type" in data

    profile = client.get("/api/v1/user/profile", headers=headers).json()
    assert profile["avatar_url"] == data["avatar_url"]


def test_avatar_generate_rejects_unsupported_mime_type():
    headers = {"Authorization": "Bearer mock_token_avatarmimeuser"}
    response = client.post(
        "/api/v1/user/avatar/generate",
        headers=headers,
        json={"description": "test", "photo_mime_type": "image/gif"},
    )
    assert response.status_code == 422
