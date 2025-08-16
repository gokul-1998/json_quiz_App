import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the app correctly
from main import app

client = TestClient(app)

def test_login_google():
    """Test the Google OAuth2 login endpoint"""
    response = client.get("/auth/login")
    assert response.status_code == 200
    # Check that it's a redirect response
    assert response.headers["location"].startswith("https://accounts.google.com/o/oauth2/auth")

@patch("routers.auth.httpx.AsyncClient.post")
@patch("routers.auth.httpx.AsyncClient.get")
@patch("auth_utils.get_user_by_google_id")
@patch("auth_utils.create_user")
@patch("auth_utils.create_access_token")
def test_callback_success(
    mock_create_access_token,
    mock_create_user,
    mock_get_user_by_google_id,
    mock_httpx_get,
    mock_httpx_post
):
    """Test the Google OAuth2 callback endpoint with successful authentication"""
    # Mock the token response
    mock_token_response = Mock()
    mock_token_response.json.return_value = {"access_token": "test_access_token"}
    mock_httpx_post.return_value = mock_token_response
    
    # Mock the user info response
    mock_user_info_response = Mock()
    mock_user_info_response.json.return_value = {
        "id": "123456789",
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/picture.jpg"
    }
    mock_httpx_get.return_value = mock_user_info_response
    
    # Mock user lookup
    mock_user = Mock()
    mock_user.id = 1
    mock_user.email = "test@example.com"
    mock_get_user_by_google_id.return_value = mock_user
    
    # Mock access token creation
    mock_create_access_token.return_value = "test_jwt_token"
    
    # Make the request
    response = client.get("/auth/callback?code=test_code")
    
    # Check the response
    assert response.status_code == 200
    assert "test_jwt_token" in response.headers["location"]

def test_logout():
    """Test the logout endpoint"""
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Logged out successfully"}

@patch("routers.auth.jwt.decode")
@patch("auth_utils.get_user_by_email")
def test_get_user_success(mock_get_user_by_email, mock_jwt_decode):
    """Test getting user info with valid token"""
    # Mock JWT decode
    mock_jwt_decode.return_value = {"sub": "test@example.com"}
    
    # Mock user lookup
    mock_user = Mock()
    mock_user.id = 1
    mock_user.email = "test@example.com"
    mock_user.name = "Test User"
    mock_get_user_by_email.return_value = mock_user
    
    # Make the request
    response = client.get("/auth/user", headers={"Authorization": "Bearer test_token"})
    
    # Check the response
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

@patch("routers.auth.jwt.decode")
def test_get_user_invalid_token(mock_jwt_decode):
    """Test getting user info with invalid token"""
    # Mock JWT decode to raise an exception
    mock_jwt_decode.side_effect = Exception("Invalid token")
    
    # Make the request
    response = client.get("/auth/user", headers={"Authorization": "Bearer invalid_token"})
    
    # Check the response
    assert response.status_code == 401

@patch("routers.auth.jwt.decode")
@patch("auth_utils.get_user_by_email")
def test_get_user_not_found(mock_get_user_by_email, mock_jwt_decode):
    """Test getting user info when user is not found"""
    # Mock JWT decode
    mock_jwt_decode.return_value = {"sub": "nonexistent@example.com"}
    
    # Mock user lookup to return None
    mock_get_user_by_email.return_value = None
    
    # Make the request
    response = client.get("/auth/user", headers={"Authorization": "Bearer test_token"})
    
    # Check the response
    assert response.status_code == 404