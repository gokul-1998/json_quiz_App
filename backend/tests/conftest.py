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

# Override get_current_user for tests
def override_get_current_user():
    """Override get_current_user for tests"""
    def fake_user(*args, **kwargs):
        return None  # Will be replaced by the test's mock
    return fake_user

# Create a test database and session maker
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create tables
Base.metadata.create_all(bind=test_engine)

@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database session for each test"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()  # Roll back any changes
        db.close()

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
def client(test_db, test_user):
    """Create a test client for the FastAPI app"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    def override_current_user():
        return test_user
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

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