import pytest
from API.Database.Models import User


def test_create_user(test_client, session):
    response = test_client.post(
        "/users/",
        json={"username": "newuser", "email": "newuser@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"

def test_user_persistance(session):
    user = session.query(User).filter(User.username == "newuser").first()
    assert user is not None
    assert user.email == "newuser@example.com"

def test_login_user(test_client, session):
    response = test_client.post(
        "/token", 
        data={"username": "newuser", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_user_details(test_client, session):
    login_response = test_client.post(
        "/token", 
        data={"username": "newuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"

def test_create_seance(test_client, session):
    login_response = test_client.post(
        "/token", 
        data={"username": "newuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    seance_data = {
        "user_id": 1,
        "temp_C": 22.5,
        "wind_speed": 10.0,
        "wind_gust": 15.0,
        "wind_dir": 180,
        "pressure": 1015,
        "precipitation": 0.0,
    }
    response = test_client.post("/seances/", json=seance_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["temp_C"] == 22.5

def test_get_setups(test_client, session):
    login_response = test_client.post(
        "/token", 
        data={"username": "newuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get("/setups/1/", headers=headers)
    assert response.status_code == 200

