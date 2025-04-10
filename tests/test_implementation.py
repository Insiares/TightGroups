# tests/test_implementation.py
import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from API.routes import app
from loguru import logger
import API.datamodels as dm
# client = TestClient(app)
from API.Database.Models import Seance
def test_health_endpoint(client):
    response = client.get("/health/")
    assert response.status_code == 200
    assert "status" in response.json()

def test_user_creation_flow(client, mock_db, refresh_tokens_dict):
    # 1. Create a user
    user_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "securepassword123"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    # logger.debug(f"Created user {response.json()}")
    assert response.json()["username"] == "testuser"
    assert "password_hash" not in response.json()  # Make sure password isn't returned
    
    # 2. Login with the user
    login_data = {
        "username": "testuser",
        "password": "securepassword123"
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    # logger.debug(f"Received tokens: {tokens}")
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert "token_type" in tokens
    assert "user_id" in tokens
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 3. Create a seance
    seance_data = {
        "user_id": tokens["user_id"],
        "temp_C": 22.5,
        "wind_speed": 8.0,
        "wind_gust": 12.0,
        "wind_dir": 90.0,
        "pressure": 1012.0,
        "precipitation": 0.0
    }
    response = client.post("/seances/", json=seance_data, headers=headers)
    assert response.status_code == 200
    # logger.debug(f"Created seance {response.json()}")
    assert response.json()["temp_C"] == 22.5
    mock_db.query.return_value.filter.return_value.all.return_value = [ seance_data] 
    # 4. Get seances
    response = client.get("/seances/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1
    mock_db.query.return_value.filter.return_value.first.return_value = dm.Ammo(name="Test Ammo", id=1)
    # 5. Create a setup
    setup_data = {
        "user_id": tokens["user_id"],
        "name": "Test Setup",
        "gear": "Test Rifle",
        "ammo": "Test Ammo",
        "position": "Prone",
        "drills": "Target Practice"
    }
    response = client.post("/setups/", json=setup_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Setup"
    mock_db.query.return_value.add_column.return_value.join.return_value.filter.return_value.all.return_value = [ (dm.Setup(**setup_data), "ammo_test_name")]
    # 6. Get setups
    response = client.get("/setups/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1
    
    # 7. Get gears
    response = client.get("/gears/", headers=headers)
    assert response.status_code == 200
    
    # 8. Refresh token
    with patch('API.routes.verify_token') as mock_verify:
        mock_verify.return_value = {"sub": "2"}
        with patch('API.routes.refresh_tokens_dict') as mock_dict:
            mock_dict.get.return_value = refresh_token
        # mock_encode = patch('jwt.encode')
        # mock_encode.return_value = {"sub": "2"}
            logger.debug(refresh_token)
            refresh_data = {"refresh_token": refresh_token}
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.post("/refresh", json=refresh_data, headers=headers)
            assert response.status_code == 200
            new_tokens = response.json()
            assert "access_token" in new_tokens
            assert "refresh_token" in new_tokens
        
    # 9. Logout
    logout_data = {"refresh_token": new_tokens["refresh_token"]}
    response = client.post("/logout", json=logout_data, headers={"Authorization": f"Bearer {new_tokens['access_token']}"})
    assert response.status_code == 200
    assert "message" in response.json()

