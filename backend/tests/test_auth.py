import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health", headers={"X-Request-ID": "test-request-id"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["X-Request-ID"] == "test-request-id"
    assert response.headers["X-Content-Type-Options"] == "nosniff"

def test_mock_google_auth():
    response = client.post(
        "/api/v1/auth/google",
        json={"id_token": "mock_token_testuser"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user_id"] == "usr_testuser"
    assert data["is_new_user"] is True or data["is_new_user"] is False

def test_email_register_and_login():
    # Register
    response = client.post(
        "/api/v1/auth/email/register",
        json={
            "email": "tester@alterlife.io",
            "password": "securepassword123",
            "display_name": "Tester User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["is_new_user"] is True

    # Login
    response_login = client.post(
        "/api/v1/auth/email/login",
        json={
            "email": "tester@alterlife.io",
            "password": "securepassword123"
        }
    )
    assert response_login.status_code == 200
    data_login = response_login.json()
    assert "access_token" in data_login
    assert data_login["is_new_user"] is False

    wrong_password = client.post(
        "/api/v1/auth/email/login",
        json={"email": "tester@alterlife.io", "password": "definitely-wrong"},
    )
    assert wrong_password.status_code == 401


def test_protected_endpoint_requires_authentication():
    response = client.get("/api/v1/user/profile")
    assert response.status_code == 401


def test_profile_update_and_account_deletion():
    registration = client.post(
        "/api/v1/auth/email/register",
        json={
            "email": "account-lifecycle@alterlife.io",
            "password": "securepassword123",
            "display_name": "Lifecycle User",
        },
    )
    token = registration.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    updated = client.patch(
        "/api/v1/user/profile",
        headers=headers,
        json={"display_name": "Yeni İsim", "role": "Data Engineer", "experience_years": 4},
    )
    assert updated.status_code == 200
    assert updated.json()["display_name"] == "Yeni İsim"
    assert updated.json()["role"] == "Data Engineer"

    deleted = client.delete("/api/v1/user/account", headers=headers)
    assert deleted.status_code == 200
    assert deleted.json()["status"] == "deleted"


def test_profile_daily_preferences_saved():
    headers = {"Authorization": "Bearer mock_token_prefuser"}
    client.get("/api/v1/user/profile", headers=headers)
    response = client.patch(
        "/api/v1/user/profile",
        headers=headers,
        json={
            "display_name": "Preference User",
            "daily_preferences": {
                "day_type": "busy",
                "best_focus_time": "night",
                "mood": "high",
                "available_minutes": 90,
                "include_social": False,
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["daily_preferences"]["day_type"] == "busy"
    assert data["daily_preferences"]["best_focus_time"] == "night"
