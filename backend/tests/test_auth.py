import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

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
