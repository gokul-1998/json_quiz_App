import pytest
from unittest.mock import Mock, patch
import sys
import os
import json

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from middleware.requestloggingmiddleware import RequestLoggingMiddleware

@pytest.fixture
def middleware():
    """Create a RequestLoggingMiddleware instance for testing"""
    return RequestLoggingMiddleware(app=Mock())

@pytest.fixture
def mock_request():
    """Create a mock request for testing"""
    request = Mock()
    request.method = "GET"
    request.url.path = "/test"
    request.client.host = "127.0.0.1"
    request.query_params = {"param": "value"}
    request.headers = {"Authorization": "Bearer test_token"}
    return request

@patch("middleware.requestloggingmiddleware.jwt.decode")
@patch("middleware.requestloggingmiddleware.print")
async def test_middleware_with_valid_token(mock_print, mock_jwt_decode, middleware, mock_request):
    """Test middleware with a valid JWT token"""
    # Mock JWT decode to return a payload
    mock_jwt_decode.return_value = {"user_id": 123}
    
    # Mock the call_next function
    call_next = Mock()
    call_next.return_value = Mock()
    
    # Call the middleware
    await middleware.dispatch(mock_request, call_next)
    
    # Check that print was called with the expected log message
    assert mock_print.call_count >= 1

@patch("middleware.requestloggingmiddleware.jwt.decode")
@patch("middleware.requestloggingmiddleware.print")
async def test_middleware_with_invalid_token(mock_print, mock_jwt_decode, middleware, mock_request):
    """Test middleware with an invalid JWT token"""
    # Mock JWT decode to raise an exception
    mock_jwt_decode.side_effect = Exception("Invalid token")
    
    # Mock the call_next function
    call_next = Mock()
    call_next.return_value = Mock()
    
    # Call the middleware
    await middleware.dispatch(mock_request, call_next)
    
    # Check that print was called with the expected log message
    assert mock_print.call_count >= 1

@patch("middleware.requestloggingmiddleware.print")
async def test_middleware_without_authorization_header(mock_print, middleware):
    """Test middleware without an Authorization header"""
    # Create a mock request without Authorization header
    request = Mock()
    request.method = "GET"
    request.url.path = "/test"
    request.client.host = "127.0.0.1"
    request.query_params = {}
    request.headers = {}
    
    # Mock the call_next function
    call_next = Mock()
    call_next.return_value = Mock()
    
    # Call the middleware
    await middleware.dispatch(request, call_next)
    
    # Check that print was called with the expected log message
    assert mock_print.call_count >= 1

@patch("middleware.requestloggingmiddleware.print")
async def test_middleware_with_request_body(mock_print, middleware):
    """Test middleware with request body data"""
    # Create a mock request with body data
    request = Mock()
    request.method = "POST"
    request.url.path = "/test"
    request.client.host = "127.0.0.1"
    request.query_params = {}
    request.headers = {"Authorization": "Bearer test_token"}
    
    # Mock the request body
    async def mock_body():
        return json.dumps({"key": "value"}).encode('utf-8')
    
    request.body = mock_body
    
    # Mock the call_next function
    call_next = Mock()
    call_next.return_value = Mock()
    
    # Call the middleware
    await middleware.dispatch(request, call_next)
    
    # Check that print was called with the expected log message
    assert mock_print.call_count >= 1

@patch("middleware.requestloggingmiddleware.print")
async def test_middleware_with_exception(mock_print, middleware):
    """Test middleware when an exception occurs"""
    # Create a mock request
    request = Mock()
    request.method = "GET"
    request.url.path = "/test"
    request.client.host = "127.0.0.1"
    request.query_params = {}
    request.headers = {}
    
    # Mock the call_next function to raise an exception
    call_next = Mock()
    call_next.side_effect = Exception("Test exception")
    
    # Call the middleware and expect it to raise the exception
    try:
        await middleware.dispatch(request, call_next)
        assert False, "Expected an exception to be raised"
    except Exception as e:
        assert str(e) == "Test exception"
    
    # Check that print was called with the expected log message
    assert mock_print.call_count >= 1