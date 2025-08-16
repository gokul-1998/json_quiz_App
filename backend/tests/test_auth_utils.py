import pytest
from unittest.mock import Mock, patch
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth_utils import (
    create_access_token,
    get_user_by_email,
    get_user_by_google_id,
    create_user,
    authenticate_user
)

def test_create_access_token():
    """Test creating an access token"""
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0

def test_create_access_token_with_expiration():
    """Test creating an access token with custom expiration"""
    data = {"sub": "test@example.com"}
    expires_delta = timedelta(minutes=15)
    token = create_access_token(data, expires_delta)
    assert isinstance(token, str)
    assert len(token) > 0

@patch("auth_utils.models.User")
def test_get_user_by_email(mock_user_model):
    """Test getting a user by email"""
    # Mock the query result
    mock_user = Mock()
    mock_user.email = "test@example.com"
    mock_user_model.query.filter.return_value.first.return_value = mock_user
    
    # Create a mock database session
    mock_db = Mock()
    
    # Call the function
    user = get_user_by_email(mock_db, "test@example.com")
    
    # Check the result
    assert user is not None
    assert user.email == "test@example.com"

@patch("auth_utils.models.User")
def test_get_user_by_google_id(mock_user_model):
    """Test getting a user by Google ID"""
    # Mock the query result
    mock_user = Mock()
    mock_user.google_id = "123456789"
    mock_user_model.query.filter.return_value.first.return_value = mock_user
    
    # Create a mock database session
    mock_db = Mock()
    
    # Call the function
    user = get_user_by_google_id(mock_db, "123456789")
    
    # Check the result
    assert user is not None
    assert user.google_id == "123456789"

@patch("auth_utils.models.User")
def test_create_user(mock_user_model):
    """Test creating a user"""
    # Mock the user creation
    mock_user = Mock()
    mock_user.google_id = "123456789"
    mock_user.email = "test@example.com"
    mock_user.name = "Test User"
    mock_user.picture = "https://example.com/picture.jpg"
    mock_user_model.return_value = mock_user
    
    # Create a mock database session
    mock_db = Mock()
    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.refresh = Mock()
    
    # Create a mock user schema
    mock_user_schema = Mock()
    mock_user_schema.google_id = "123456789"
    mock_user_schema.email = "test@example.com"
    mock_user_schema.name = "Test User"
    mock_user_schema.picture = "https://example.com/picture.jpg"
    
    # Call the function
    user = create_user(mock_db, mock_user_schema)
    
    # Check the result
    assert user is not None
    assert user.email == "test@example.com"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@patch("auth_utils.get_user_by_email")
def test_authenticate_user_success(mock_get_user_by_email):
    """Test authenticating a user successfully"""
    # Mock the user lookup
    mock_user = Mock()
    mock_user.email = "test@example.com"
    mock_get_user_by_email.return_value = mock_user
    
    # Create a mock database session
    mock_db = Mock()
    
    # Call the function
    user = authenticate_user(mock_db, "test@example.com")
    
    # Check the result
    assert user is not False
    assert user.email == "test@example.com"

@patch("auth_utils.get_user_by_email")
def test_authenticate_user_failure(mock_get_user_by_email):
    """Test authenticating a user that doesn't exist"""
    # Mock the user lookup to return None
    mock_get_user_by_email.return_value = None
    
    # Create a mock database session
    mock_db = Mock()
    
    # Call the function
    user = authenticate_user(mock_db, "nonexistent@example.com")
    
    # Check the result
    assert user is False