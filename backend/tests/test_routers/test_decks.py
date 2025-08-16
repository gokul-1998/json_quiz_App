import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the app correctly
from main import app
from models import User, Deck, Card, DeckCollaborator
from schemas import DeckVisibility

def test_test_deck_route(client):
    """Test the test deck route"""
    response = client.get("/decks/test")
    assert response.status_code == 200
    assert response.json() == {"message": "Deck router is working"}

def test_create_deck_success(client, test_db, test_user):
    """Test creating a deck successfully"""
    
    # Make the request
    response = client.post(
        "/decks/",
        json={
            "title": "Test Deck",
            "description": "A test deck",
            "visibility": "private"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Check the response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["title"] == "Test Deck"
    assert response_data["owner_id"] == test_user.id

@patch("routers.decks.get_current_user")
def test_get_decks_success(mock_get_current_user, client, test_db):
    """Test getting all decks for a user"""
    # Create a test user
    test_user = User()
    test_user.email = "test@example.com"
    test_user.google_id = "123"
    test_user.name = "Test User"
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)
    
    # Create a test deck
    test_deck = Deck()
    test_deck.title = "Test Deck"
    test_deck.description = "Test Description"
    test_deck.visibility = DeckVisibility.PRIVATE
    test_deck.owner_id = test_user.id
    test_db.add(test_deck)
    test_db.commit()
    
    # Mock the current user
    mock_get_current_user.return_value = test_user
    
    # Make the request
    response = client.get("/decks/", headers={"Authorization": "Bearer test_token"})
    
    # Check the response
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test Deck"

@patch("routers.decks.get_current_user")
def test_get_deck_success(mock_get_current_user, client, test_db):
    """Test getting a specific deck"""
    # Create a test user
    test_user = User()
    test_user.email = "test@example.com"
    test_user.google_id = "123"
    test_user.name = "Test User"
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)
    
    # Create a test deck
    test_deck = Deck()
    test_deck.title = "Test Deck"
    test_deck.description = "Test Description"
    test_deck.visibility = DeckVisibility.PRIVATE
    test_deck.owner_id = test_user.id
    test_db.add(test_deck)
    test_db.commit()
    
    # Mock the current user
    mock_get_current_user.return_value = test_user
    
    # Make the request
    response = client.get(f"/decks/{test_deck.id}", headers={"Authorization": "Bearer test_token"})
    
    # Check the response
    assert response.status_code == 200
    assert response.json()["title"] == "Test Deck"

@patch("routers.decks.get_current_user")
def test_update_deck_success(mock_get_current_user, client, test_db):
    """Test updating a deck"""
    # Create a test user
    test_user = User()
    test_user.email = "test@example.com"
    test_user.google_id = "123"
    test_user.name = "Test User"
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)
    
    # Create a test deck
    test_deck = Deck()
    test_deck.title = "Test Deck"
    test_deck.description = "Test Description"
    test_deck.visibility = DeckVisibility.PRIVATE
    test_deck.owner_id = test_user.id
    test_db.add(test_deck)
    test_db.commit()
    
    # Mock the current user
    mock_get_current_user.return_value = test_user
    
    # Make the request
    response = client.put(
        f"/decks/{test_deck.id}",
        json={
            "title": "Updated Test Deck",
            "description": "An updated test deck",
            "visibility": "public"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Check the response
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Test Deck"

@patch("routers.decks.get_current_user")
@patch("routers.decks.models.Deck")
def test_get_deck_success(mock_deck_model, mock_get_current_user):
    """Test getting a specific deck by ID"""
    # Mock the current user
    mock_user = Mock()
    mock_user.id = 1
    mock_get_current_user.return_value = mock_user
    
    # Mock the deck
    mock_deck = Mock()
    mock_deck.id = 1
    mock_deck.title = "Test Deck"
    mock_deck.owner_id = 1
    mock_deck_model.query.filter.return_value.first.return_value = mock_deck
    
    # Make the request
    response = client.get("/decks/1", headers={"Authorization": "Bearer test_token"})
    
    # Check the response
    assert response.status_code == 200
    assert response.json()["id"] == 1

@patch("routers.decks.get_current_user")
@patch("routers.decks.models.Deck")
def test_update_deck_success(mock_deck_model, mock_get_current_user):
    """Test updating a deck"""
    # Mock the current user
    mock_user = Mock()
    mock_user.id = 1
    mock_get_current_user.return_value = mock_user
    
    # Mock the deck
    mock_deck = Mock()
    mock_deck.id = 1
    mock_deck.owner_id = 1
    mock_deck_model.query.filter.return_value.first.return_value = mock_deck
    
    # Make the request
    response = client.put(
        "/decks/1",
        json={
            "title": "Updated Deck",
            "description": "An updated test deck"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Check the response
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Deck"

@patch("routers.decks.get_current_user")
@patch("routers.decks.models.Deck")
def test_delete_deck_success(mock_deck_model, mock_get_current_user):
    """Test deleting a deck"""
    # Mock the current user
    mock_user = Mock()
    mock_user.id = 1
    mock_get_current_user.return_value = mock_user
    
    # Mock the deck
    mock_deck = Mock()
    mock_deck.id = 1
    mock_deck.owner_id = 1
    mock_deck_model.query.filter.return_value.first.return_value = mock_deck
    
    # Make the request
    response = client.delete("/decks/1", headers={"Authorization": "Bearer test_token"})
    
    # Check the response
    assert response.status_code == 200
    assert response.json() == {"message": "Deck deleted successfully"}

@patch("routers.decks.get_current_user")
@patch("routers.decks.models.Deck")
def test_create_card_success(mock_deck_model, mock_get_current_user):
    """Test creating a card in a deck"""
    # Mock the current user
    mock_user = Mock()
    mock_user.id = 1
    mock_get_current_user.return_value = mock_user
    
    # Mock the deck
    mock_deck = Mock()
    mock_deck.id = 1
    mock_deck.owner_id = 1
    mock_deck_model.query.filter.return_value.first.return_value = mock_deck
    
    # Make the request
    response = client.post(
        "/decks/1/cards",
        json={
            "front_content": "Front content",
            "back_content": "Back content"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Check the response
    assert response.status_code == 200
    assert response.json()["front_content"] == "Front content"

@patch("routers.decks.get_current_user")
@patch("routers.decks.models.Deck")
@patch("routers.decks.models.Card")
def test_get_cards_success(mock_card_model, mock_deck_model, mock_get_current_user):
    """Test getting all cards in a deck"""
    # Mock the current user
    mock_user = Mock()
    mock_user.id = 1
    mock_get_current_user.return_value = mock_user
    
    # Mock the deck
    mock_deck = Mock()
    mock_deck.id = 1
    mock_deck.owner_id = 1
    mock_deck_model.query.filter.return_value.first.return_value = mock_deck
    
    # Mock the cards
    mock_card = Mock()
    mock_card.id = 1
    mock_card.front_content = "Front content"
    mock_card.back_content = "Back content"
    mock_card.deck_id = 1
    mock_card_model.query.filter.return_value.offset.return_value.limit.return_value.all.return_value = [mock_card]
    
    # Make the request
    response = client.get("/decks/1/cards", headers={"Authorization": "Bearer test_token"})
    
    # Check the response
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

@patch("routers.decks.get_current_user")
@patch("routers.decks.models.Deck")
@patch("routers.decks.models.Card")
def test_update_card_success(mock_card_model, mock_deck_model, mock_get_current_user):
    """Test updating a card"""
    # Mock the current user
    mock_user = Mock()
    mock_user.id = 1
    mock_get_current_user.return_value = mock_user
    
    # Mock the deck
    mock_deck = Mock()
    mock_deck.id = 1
    mock_deck.owner_id = 1
    mock_deck_model.query.filter.return_value.first.return_value = mock_deck
    
    # Mock the card
    mock_card = Mock()
    mock_card.id = 1
    mock_card.deck_id = 1
    mock_card_model.query.filter.return_value.first.return_value = mock_card
    
    # Make the request
    response = client.put(
        "/decks/1/cards/1",
        json={
            "front_content": "Updated front content",
            "back_content": "Updated back content"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Check the response
    assert response.status_code == 200
    assert response.json()["front_content"] == "Updated front content"

@patch("routers.decks.get_current_user")
@patch("routers.decks.models.Deck")
@patch("routers.decks.models.Card")
def test_delete_card_success(mock_card_model, mock_deck_model, mock_get_current_user):
    """Test deleting a card"""
    # Mock the current user
    mock_user = Mock()
    mock_user.id = 1
    mock_get_current_user.return_value = mock_user
    
    # Mock the deck
    mock_deck = Mock()
    mock_deck.id = 1
    mock_deck.owner_id = 1
    mock_deck_model.query.filter.return_value.first.return_value = mock_deck
    
    # Mock the card
    mock_card = Mock()
    mock_card.id = 1
    mock_card.deck_id = 1
    mock_card_model.query.filter.return_value.first.return_value = mock_card
    
    # Make the request
    response = client.delete("/decks/1/cards/1", headers={"Authorization": "Bearer test_token"})
    
    # Check the response
    assert response.status_code == 200
    assert response.json() == {"message": "Card deleted successfully"}

@patch("routers.decks.get_current_user")
@patch("routers.decks.models.Deck")
@patch("routers.decks.models.User")
def test_add_collaborator_success(mock_user_model, mock_deck_model, mock_get_current_user):
    """Test adding a collaborator to a deck"""
    # Mock the current user
    mock_user = Mock()
    mock_user.id = 1
    mock_get_current_user.return_value = mock_user
    
    # Mock the deck
    mock_deck = Mock()
    mock_deck.id = 1
    mock_deck.owner_id = 1
    mock_deck_model.query.filter.return_value.first.return_value = mock_deck
    
    # Mock the user to add as collaborator
    mock_collaborator_user = Mock()
    mock_collaborator_user.id = 2
    mock_user_model.query.filter.return_value.first.return_value = mock_collaborator_user
    
    # Make the request
    response = client.post(
        "/decks/1/collaborators",
        json={"deck_id": 1, "user_id": 2},
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Check the response
    assert response.status_code == 200

@patch("routers.decks.get_current_user")
@patch("routers.decks.models.Deck")
@patch("routers.decks.models.DeckCollaborator")
def test_remove_collaborator_success(mock_collaborator_model, mock_deck_model, mock_get_current_user):
    """Test removing a collaborator from a deck"""
    # Mock the current user
    mock_user = Mock()
    mock_user.id = 1
    mock_get_current_user.return_value = mock_user
    
    # Mock the deck
    mock_deck = Mock()
    mock_deck.id = 1
    mock_deck.owner_id = 1
    mock_deck_model.query.filter.return_value.first.return_value = mock_deck
    
    # Mock the collaborator
    mock_collaborator = Mock()
    mock_collaborator.deck_id = 1
    mock_collaborator.user_id = 2
    mock_collaborator_model.query.filter.return_value.first.return_value = mock_collaborator
    
    # Make the request
    response = client.delete("/decks/1/collaborators/2", headers={"Authorization": "Bearer test_token"})
    
    # Check the response
    assert response.status_code == 200
    assert response.json() == {"message": "Collaborator removed successfully"}

@patch("routers.decks.get_current_user")
@patch("routers.decks.models.Deck")
@patch("routers.decks.models.DeckCollaborator")
def test_get_collaborators_success(mock_collaborator_model, mock_deck_model, mock_get_current_user):
    """Test getting all collaborators for a deck"""
    # Mock the current user
    mock_user = Mock()
    mock_user.id = 1
    mock_get_current_user.return_value = mock_user
    
    # Mock the deck
    mock_deck = Mock()
    mock_deck.id = 1
    mock_deck.owner_id = 1
    mock_deck_model.query.filter.return_value.first.return_value = mock_deck
    
    # Mock the collaborators
    mock_collaborator = Mock()
    mock_collaborator.id = 1
    mock_collaborator.deck_id = 1
    mock_collaborator.user_id = 2
    mock_collaborator_model.query.filter.return_value.all.return_value = [mock_collaborator]
    
    # Make the request
    response = client.get("/decks/1/collaborators", headers={"Authorization": "Bearer test_token"})
    
    # Check the response
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0