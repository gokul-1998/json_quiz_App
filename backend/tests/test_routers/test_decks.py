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

def test_create_deck_success(client, test_db, test_user, test_auth_headers):
    """Test creating a deck successfully"""
    
    # Make the request
    response = client.post(
        "/decks/",
        json={
            "title": "Test Deck",
            "description": "A test deck",
            "visibility": "private"
        },
        headers=test_auth_headers
    )
    
    # Check the response
    assert response.status_code == 200, f"Response: {response.json()}"
    response_data = response.json()
    assert response_data["title"] == "Test Deck"
    
    # Verify the deck was created in the database
    deck = test_db.query(Deck).first()
    assert deck is not None
    assert deck.title == "Test Deck"
    assert deck.owner_id == test_user.id

@patch("routers.decks.get_current_user")
def test_get_decks_success(mock_get_current_user, client, test_db, test_user):
    """Test getting all decks for a user"""
    
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
def test_get_deck_success(mock_get_current_user, client, test_db, test_user):
    """Test getting a specific deck"""
    
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
def test_update_deck_success(mock_get_current_user, client, test_db, test_user):
    """Test updating a deck"""
    
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





def test_delete_deck_success(client, test_db, test_user, test_auth_headers):
    """Test deleting a deck"""
    # Create a test deck
    test_deck = Deck(
        title="Test Deck for Deletion",
        description="A deck to be deleted",
        owner_id=test_user.id
    )
    test_db.add(test_deck)
    test_db.commit()
    test_db.refresh(test_deck)

    # Make the request to delete the deck
    response = client.delete(f"/decks/{test_deck.id}", headers=test_auth_headers)

    # Check the response
    assert response.status_code == 200, f"Response: {response.json()}"
    assert response.json() == {"message": "Deck deleted successfully"}

    # Verify the deck was deleted from the database
    deck = test_db.query(Deck).filter(Deck.id == test_deck.id).first()
    assert deck is None

def test_create_card_success(client, test_db, test_user, test_auth_headers):
    """Test creating a card in a deck"""
    # Create a test deck
    test_deck = Deck(title="Test Deck", owner_id=test_user.id)
    test_db.add(test_deck)
    test_db.commit()
    test_db.refresh(test_deck)

    # Make the request
    response = client.post(
        f"/decks/{test_deck.id}/cards",
        json={"front_content": "Front", "back_content": "Back"},
        headers=test_auth_headers
    )

    # Check the response
    assert response.status_code == 200, f"Response: {response.json()}"
    data = response.json()
    assert data["front_content"] == "Front"

    # Verify in DB
    card = test_db.query(Card).first()
    assert card is not None
    assert card.deck_id == test_deck.id

def test_get_cards_success(client, test_db, test_user, test_auth_headers):
    """Test getting all cards in a deck"""
    # Create a test deck and card
    test_deck = Deck(title="Test Deck", owner_id=test_user.id)
    test_card = Card(front_content="Front", back_content="Back", deck=test_deck)
    test_db.add_all([test_deck, test_card])
    test_db.commit()
    test_db.refresh(test_deck)

    # Make the request
    response = client.get(f"/decks/{test_deck.id}/cards", headers=test_auth_headers)

    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["front_content"] == "Front"

def test_update_card_success(client, test_db, test_user, test_auth_headers):
    """Test updating a card"""
    # Create a test deck and card
    test_deck = Deck(title="Test Deck", owner_id=test_user.id)
    test_card = Card(front_content="Front", back_content="Back", deck=test_deck)
    test_db.add_all([test_deck, test_card])
    test_db.commit()
    test_db.refresh(test_card)

    # Make the request
    response = client.put(
        f"/decks/{test_deck.id}/cards/{test_card.id}",
        json={"front_content": "Updated"},
        headers=test_auth_headers
    )

    # Check the response
    assert response.status_code == 200, f"Response: {response.json()}"
    data = response.json()
    assert data["front_content"] == "Updated"

    # Verify the change in the database
    test_db.refresh(test_card)
    assert test_card.front_content == "Updated"

def test_delete_card_success(client, test_db, test_user, test_auth_headers):
    """Test deleting a card"""
    # Create a test deck and card
    test_deck = Deck(title="Test Deck", owner_id=test_user.id)
    test_card = Card(front_content="Front", back_content="Back", deck=test_deck)
    test_db.add_all([test_deck, test_card])
    test_db.commit()
    test_db.refresh(test_card)

    # Make the request
    response = client.delete(f"/decks/{test_deck.id}/cards/{test_card.id}", headers=test_auth_headers)

    # Check the response
    assert response.status_code == 200
    assert test_db.query(Card).count() == 0

def test_add_collaborator_success(client, test_db, test_user, test_auth_headers):
    """Test adding a collaborator to a deck"""
    # Create a deck and a user to be a collaborator
    deck = Deck(title="Test Deck", owner_id=test_user.id)
    collaborator_user = User(email="collab@example.com", name="Collaborator", google_id="456")
    test_db.add_all([deck, collaborator_user])
    test_db.commit()
    test_db.refresh(deck)
    test_db.refresh(collaborator_user)

    # Make the request
    response = client.post(
        f"/decks/{deck.id}/collaborators",
        json={"user_id": collaborator_user.id},
        headers=test_auth_headers
    )

    # Check the response
    assert response.status_code == 200, f"Response: {response.json()}"
    assert test_db.query(DeckCollaborator).count() == 1

def test_remove_collaborator_success(client, test_db, test_user, test_auth_headers):
    """Test removing a collaborator from a deck"""
    # Create a deck, a collaborator user, and the collaboration
    deck = Deck(title="Test Deck", owner_id=test_user.id)
    collaborator_user = User(email="collab@example.com", name="Collaborator", google_id="456")
    collaboration = DeckCollaborator(deck=deck, user=collaborator_user)
    test_db.add_all([deck, collaborator_user, collaboration])
    test_db.commit()
    test_db.refresh(deck)
    test_db.refresh(collaborator_user)

    # Make the request
    response = client.delete(
        f"/decks/{deck.id}/collaborators/{collaborator_user.id}",
        headers=test_auth_headers
    )

    # Check the response
    assert response.status_code == 200, f"Response: {response.json()}"
    assert test_db.query(DeckCollaborator).count() == 0

def test_get_collaborators_success(client, test_db, test_user, test_auth_headers):
    """Test getting all collaborators for a deck"""
    # Create a deck, a collaborator user, and the collaboration
    deck = Deck(title="Test Deck", owner_id=test_user.id)
    collaborator_user = User(email="collab@example.com", name="Collaborator", google_id="456")
    collaboration = DeckCollaborator(deck=deck, user=collaborator_user)
    test_db.add_all([deck, collaborator_user, collaboration])
    test_db.commit()
    test_db.refresh(deck)

    # Make the request
    response = client.get(f"/decks/{deck.id}/collaborators", headers=test_auth_headers)

    # Check the response
    assert response.status_code == 200, f"Response: {response.json()}"
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["user"]["email"] == collaborator_user.email