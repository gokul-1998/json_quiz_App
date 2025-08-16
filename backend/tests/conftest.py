import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os
from typing import Generator
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the app correctly
from main import app
from database import Base, get_db
from models import User, Deck, Card, DeckCollaborator
from routers.decks import get_current_user

# Create the test engine
engine = create_engine(
    "sqlite:///./test.db",  # Use a file instead of memory for debugging
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database"""
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        yield
    finally:
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_db():
    """Get database session for testing"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    user = User()
    user.email = "test@example.com"
    user.google_id = "123"
    user.name = "Test User"
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def test_auth_headers():
    """Create test authentication headers"""
    return {"Authorization": "Bearer test_token"}

@pytest.fixture
def test_app(test_db):
    """Create test FastAPI app with overridden dependencies"""
    def _override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    return app

@pytest.fixture
def client(test_app, test_user):
    """Create test client"""
    def override_get_current_user():
        return test_user

    test_app.dependency_overrides[get_current_user] = override_get_current_user
    
    with TestClient(test_app) as client:
        yield client
    
    test_app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def db_session():
    """Create a database session for testing"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    return Mock(
        id=1,
        google_id="123456789",
        email="test@example.com",
        name="Test User",
        picture="https://example.com/picture.jpg",
        is_active=True
    )

@pytest.fixture
def mock_deck(mock_user):
    """Create a mock deck for testing"""
    return Mock(
        id=1,
        title="Test Deck",
        description="A test deck",
        visibility="private",
        owner_id=mock_user.id,
        owner=mock_user
    )

@pytest.fixture
def mock_card(mock_deck):
    """Create a mock card for testing"""
    return Mock(
        id=1,
        front_content="Front content",
        back_content="Back content",
        deck_id=mock_deck.id,
        deck=mock_deck
    )

@pytest.fixture
def mock_collaborator(mock_user, mock_deck):
    """Create a mock collaborator for testing"""
    return Mock(
        id=1,
        deck_id=mock_deck.id,
        user_id=mock_user.id,
        deck=mock_deck,
        user=mock_user
    )

@pytest.fixture
def mock_jwt_token():
    """Create a mock JWT token for testing"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNjI0NTA2MzQ1fQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

@pytest.fixture
def auth_headers(mock_jwt_token):
    """Create authorization headers for testing"""
    return {"Authorization": f"Bearer {mock_jwt_token}"}