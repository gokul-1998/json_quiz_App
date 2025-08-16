import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import User, Deck, Card, DeckCollaborator

def test_user_model():
    """Test the User model"""
    user = User()
    user.id = 1
    user.google_id = "123456789"
    user.email = "test@example.com"
    user.name = "Test User"
    user.picture = "https://example.com/picture.jpg"
    user.is_active = True
    
    assert user.id == 1
    assert user.google_id == "123456789"
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.picture == "https://example.com/picture.jpg"
    assert user.is_active == True

def test_deck_model():
    """Test the Deck model"""
    deck = Deck()
    deck.id = 1
    deck.title = "Test Deck"
    deck.description = "A test deck"
    deck.visibility = "private"
    deck.owner_id = 1
    
    assert deck.id == 1
    assert deck.title == "Test Deck"
    assert deck.description == "A test deck"
    assert deck.visibility == "private"
    assert deck.owner_id == 1

def test_card_model():
    """Test the Card model"""
    card = Card()
    card.id = 1
    card.front_content = "Front content"
    card.back_content = "Back content"
    card.deck_id = 1
    
    assert card.id == 1
    assert card.front_content == "Front content"
    assert card.back_content == "Back content"
    assert card.deck_id == 1

def test_deck_collaborator_model():
    """Test the DeckCollaborator model"""
    collaborator = DeckCollaborator()
    collaborator.id = 1
    collaborator.deck_id = 1
    collaborator.user_id = 2
    
    assert collaborator.id == 1
    assert collaborator.deck_id == 1
    assert collaborator.user_id == 2