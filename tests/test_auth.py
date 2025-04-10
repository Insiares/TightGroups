# tests/test_auth.py
import pytest
from unittest.mock import patch, MagicMock
import jwt
import os
from tests.conftest import SECRET_KEY, ALGORITHM
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from API.routes import (
    authenticate_user, 
    get_user, 
    get_current_user, 
    create_access_token,
    verify_token,
    create_refresh_token,
    login_for_access_token,
    refresh_token as refresh_token_endpoint,
    logout
)



def test_authenticate_user_success(client):
    with patch('API.routes.get_user') as mock_get_user, \
         patch('API.routes.verify_password') as mock_verify_password:
        
        mock_user = MagicMock()
        mock_get_user.return_value = mock_user
        mock_verify_password.return_value = True
        
        result = authenticate_user('testuser', 'password123')
        
        assert result == mock_user
        mock_get_user.assert_called_once_with('testuser')
        mock_verify_password.assert_called_once_with('password123', mock_user.password_hash)

def test_authenticate_user_user_not_found(client):
    with patch('API.routes.get_user') as mock_get_user:
        mock_get_user.return_value = None
        
        with pytest.raises(HTTPException) as exc:
           result =  authenticate_user('nonexistent', 'password123')
        
        assert exc.value.status_code == 401
        assert exc.value.detail == "Invalid credentials"

def test_authenticate_user_invalid_password(client):
    with patch('API.routes.get_user') as mock_get_user, \
         patch('API.routes.verify_password') as mock_verify_password:
        
        mock_user = MagicMock()
        mock_get_user.return_value = mock_user
        mock_verify_password.return_value = False
        
        with pytest.raises(HTTPException) as exc:
            authenticate_user('testuser', 'wrong_password')
        

        assert exc.value.detail == "Invalid Credentials "

def test_get_current_user_valid_token(client):
    with patch('jwt.decode') as mock_decode:
        mock_decode.return_value = {'sub': 'testuser'}
        
        # Mock the token blacklist
        with patch('API.routes.token_blacklist', set()):
            result = get_current_user('valid_token')
            
            assert result == {'sub': 'testuser'}
            mock_decode.assert_called_once()

def test_get_current_user_blacklisted_token(client):
    # Mock the token blacklist with our test token
    with patch('API.routes.token_blacklist', {'blacklisted_token'}):
        with pytest.raises(HTTPException) as exc:
            get_current_user('blacklisted_token')
        
        assert exc.value.status_code == 401
        assert exc.value.detail == "Token is blacklisted"

def test_get_current_user_expired_token(client):
    with patch('jwt.decode') as mock_decode:
        mock_decode.side_effect = jwt.ExpiredSignatureError()
        
        with pytest.raises(HTTPException) as exc:
            get_current_user('expired_token')
        
        assert exc.value.status_code == 403
        assert exc.value.detail == "Token has expired. Please refresh your token."

def test_get_current_user_invalid_token(client):
    with patch('jwt.decode') as mock_decode:
        mock_decode.side_effect = jwt.InvalidTokenError()
        
        with pytest.raises(HTTPException) as exc:
            get_current_user('invalid_token')
        
        assert exc.value.status_code == 401
        assert exc.value.detail == "Invalid token. Please log in again."

def test_create_access_token(client):
    # Test with specific expiry time
    data = {"sub": "testuser"}
    delta = timedelta(minutes=30)
    
    with patch('API.routes.datetime') as mock_datetime:
        mock_now = datetime(2023, 1, 1, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now
        
        with patch('jwt.encode') as mock_encode:
            mock_encode.return_value = "test_token"
            
            token = create_access_token(data, delta)
            
            expected_expire = mock_now + delta
            expected_payload = {**data, "exp": expected_expire}
            mock_encode.assert_called_once_with(expected_payload, SECRET_KEY, algorithm=ALGORITHM)
            assert token == "test_token"

def test_login_for_access_token_success(client, mock_db):
    form_data = MagicMock()
    form_data.username = "testuser"
    form_data.password = "password123"
    
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.username = "testuser"
    
    with patch('API.routes.authenticate_user', return_value=mock_user), \
         patch('API.routes.create_access_token', return_value="test_access_token"), \
         patch('API.routes.create_refresh_token', return_value="test_refresh_token"), \
         patch('API.routes.refresh_tokens_dict', {}):
        
        response =  login_for_access_token(form_data, mock_db)
        
        assert response["access_token"] == "test_access_token"
        assert response["refresh_token"] == "test_refresh_token"
        assert response["user_id"] == mock_user.id
        assert response["token_type"] == "bearer"

def test_login_for_access_token_invalid_credentials(client, mock_db):
    form_data = MagicMock()
    form_data.username = "testuser"
    form_data.password = "wrong_password"
    
    with patch('API.routes.authenticate_user', side_effect=HTTPException(status_code=401, detail="Invalid credentials")):
        with pytest.raises(HTTPException) as exc:
             reponse = login_for_access_token(form_data, mock_db)
        
        assert exc.value.status_code == 401

