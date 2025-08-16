from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from schemas import Deck, DeckCreate, DeckUpdate, Card, CardCreate, DeckCollaborator, DeckCollaboratorCreate
from models import User, Deck as DeckModel, Card as CardModel, DeckCollaborator as DeckCollaboratorModel
from auth_utils import get_user_by_email
from database import get_db
from config import SECRET_KEY, ALGORITHM
import jwt
from jwt.exceptions import InvalidTokenError

router = APIRouter( tags=["decks"])

def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get current user from request"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        user = get_user_by_email(db, user_email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

@router.get("/test")
def test_deck_route():
    """Test route to check if the router is working"""
    return {"message": "Deck router is working"}

@router.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        # Try to query the users table
        users = db.query(User).all()
        return {"message": "Database connection successful", "user_count": len(users)}
    except Exception as e:
        return {"message": f"Database connection failed: {str(e)}"}

@router.get("/test-models")
def test_models(db: Session = Depends(get_db)):
    """Test if models are working correctly"""
    try:
        # Test creating a simple query
        query = db.query(User)
        # Try to execute the query
        result = query.first()
        return {"message": "Models are working correctly", "result": str(result)}
    except Exception as e:
        return {"message": f"Models test failed: {str(e)}"}

@router.post("/", response_model=Deck)
def create_deck(
    deck: DeckCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new deck"""
    try:
        # Create a new deck instance
        db_deck = DeckModel()
        db_deck.title = deck.title
        db_deck.description = deck.description
        db_deck.visibility = deck.visibility
        db_deck.owner_id = current_user.id
        
        db.add(db_deck)
        db.commit()
        db.refresh(db_deck)
        return db_deck
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating deck: {str(e)}"
        )

@router.get("/", response_model=List[Deck])
def get_decks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all decks for the current user"""
    try:
        decks = db.query(DeckModel).filter(
            DeckModel.owner_id == current_user.id
        ).offset(skip).limit(limit).all()
        return decks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching decks: {str(e)}"
        )

@router.get("/{deck_id}", response_model=Deck)
def get_deck(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific deck by ID"""
    try:
        deck = db.query(DeckModel).filter(DeckModel.id == deck_id).first()
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deck not found"
            )
        
        # Check if user has access to this deck
        if deck.owner_id != current_user.id:
            # Check if user is a collaborator
            collaborator = db.query(DeckCollaboratorModel).filter(
                DeckCollaboratorModel.deck_id == deck_id,
                DeckCollaboratorModel.user_id == current_user.id
            ).first()
            
            if not collaborator and deck.visibility != "public":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to access this deck"
                )
        
        return deck
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching deck: {str(e)}"
        )

@router.put("/{deck_id}", response_model=Deck)
def update_deck(
    deck_id: int,
    deck_update: DeckUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a deck"""
    try:
        db_deck = db.query(DeckModel).filter(DeckModel.id == deck_id).first()
        if not db_deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deck not found"
            )
        
        if db_deck.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to update this deck"
            )
        
        # Update deck fields
        update_data = deck_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_deck, field, value)
        
        db.commit()
        db.refresh(db_deck)
        return db_deck
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating deck: {str(e)}"
        )

@router.delete("/{deck_id}")
def delete_deck(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a deck"""
    try:
        db_deck = db.query(DeckModel).filter(DeckModel.id == deck_id).first()
        if not db_deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deck not found"
            )
        
        if db_deck.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to delete this deck"
            )
        
        db.delete(db_deck)
        db.commit()
        return {"message": "Deck deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting deck: {str(e)}"
        )

# Card routes
@router.post("/{deck_id}/cards", response_model=Card)
def create_card(
    deck_id: int,
    card: CardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new card in a deck"""
    try:
        # Check if deck exists and user has access
        deck = db.query(DeckModel).filter(DeckModel.id == deck_id).first()
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deck not found"
            )
        
        # Check if user has access to this deck
        if deck.owner_id != current_user.id:
            # Check if user is a collaborator
            collaborator = db.query(DeckCollaboratorModel).filter(
                DeckCollaboratorModel.deck_id == deck_id,
                DeckCollaboratorModel.user_id == current_user.id
            ).first()
            
            if not collaborator:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to add cards to this deck"
                )
        
        db_card = CardModel(
            front_content=card.front_content,
            back_content=card.back_content,
            deck_id=deck_id
        )
        db.add(db_card)
        db.commit()
        db.refresh(db_card)
        return db_card
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating card: {str(e)}"
        )

@router.get("/{deck_id}/cards", response_model=List[Card])
def get_cards(
    deck_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all cards in a deck"""
    try:
        # Check if deck exists and user has access
        deck = db.query(DeckModel).filter(DeckModel.id == deck_id).first()
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deck not found"
            )
        
        # Check if user has access to this deck
        if deck.owner_id != current_user.id:
            # Check if user is a collaborator
            collaborator = db.query(DeckCollaboratorModel).filter(
                DeckCollaboratorModel.deck_id == deck_id,
                DeckCollaboratorModel.user_id == current_user.id
            ).first()
            
            if not collaborator and deck.visibility != "public":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to access this deck"
                )
        
        cards = db.query(CardModel).filter(
            CardModel.deck_id == deck_id
        ).offset(skip).limit(limit).all()
        return cards
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching cards: {str(e)}"
        )

@router.put("/{deck_id}/cards/{card_id}", response_model=Card)
def update_card(
    deck_id: int,
    card_id: int,
    card_update: CardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a card"""
    try:
        # Check if deck exists and user has access
        deck = db.query(DeckModel).filter(DeckModel.id == deck_id).first()
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deck not found"
            )
        
        # Check if user has access to this deck
        if deck.owner_id != current_user.id:
            # Check if user is a collaborator
            collaborator = db.query(DeckCollaboratorModel).filter(
                DeckCollaboratorModel.deck_id == deck_id,
                DeckCollaboratorModel.user_id == current_user.id
            ).first()
            
            if not collaborator:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to update cards in this deck"
                )
        
        db_card = db.query(CardModel).filter(
            CardModel.id == card_id,
            CardModel.deck_id == deck_id
        ).first()
        
        if not db_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found"
            )
        
        # Update card fields
        update_data = card_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_card, field, value)
        
        db.commit()
        db.refresh(db_card)
        return db_card
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating card: {str(e)}"
        )

@router.delete("/{deck_id}/cards/{card_id}")
def delete_card(
    deck_id: int,
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a card"""
    try:
        # Check if deck exists and user has access
        deck = db.query(DeckModel).filter(DeckModel.id == deck_id).first()
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deck not found"
            )
        
        # Check if user has access to this deck
        if deck.owner_id != current_user.id:
            # Check if user is a collaborator
            collaborator = db.query(DeckCollaboratorModel).filter(
                DeckCollaboratorModel.deck_id == deck_id,
                DeckCollaboratorModel.user_id == current_user.id
            ).first()
            
            if not collaborator:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to delete cards from this deck"
                )
        
        db_card = db.query(CardModel).filter(
            CardModel.id == card_id,
            CardModel.deck_id == deck_id
        ).first()
        
        if not db_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found"
            )
        
        db.delete(db_card)
        db.commit()
        return {"message": "Card deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting card: {str(e)}"
        )

# Collaborator routes
@router.post("/{deck_id}/collaborators", response_model=DeckCollaborator)
def add_collaborator(
    deck_id: int,
    collaborator: DeckCollaboratorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a collaborator to a deck"""
    try:
        # Check if deck exists
        deck = db.query(DeckModel).filter(DeckModel.id == deck_id).first()
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deck not found"
            )
        
        # Check if user is the owner of the deck
        if deck.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only deck owners can add collaborators"
            )
        
        # Check if user exists
        user = db.query(User).filter(User.id == collaborator.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if collaborator already exists
        existing_collaborator = db.query(DeckCollaboratorModel).filter(
            DeckCollaboratorModel.deck_id == deck_id,
            DeckCollaboratorModel.user_id == collaborator.user_id
        ).first()
        
        if existing_collaborator:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a collaborator"
            )
        
        db_collaborator = DeckCollaboratorModel(
            deck_id=deck_id,
            user_id=collaborator.user_id
        )
        db.add(db_collaborator)
        db.commit()
        db.refresh(db_collaborator)
        return db_collaborator
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding collaborator: {str(e)}"
        )

@router.delete("/{deck_id}/collaborators/{user_id}")
def remove_collaborator(
    deck_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a collaborator from a deck"""
    try:
        # Check if deck exists
        deck = db.query(DeckModel).filter(DeckModel.id == deck_id).first()
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deck not found"
            )
        
        # Check if user is the owner of the deck
        if deck.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only deck owners can remove collaborators"
            )
        
        # Check if collaborator exists
        db_collaborator = db.query(DeckCollaboratorModel).filter(
            DeckCollaboratorModel.deck_id == deck_id,
            DeckCollaboratorModel.user_id == user_id
        ).first()
        
        if not db_collaborator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collaborator not found"
            )
        
        db.delete(db_collaborator)
        db.commit()
        return {"message": "Collaborator removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing collaborator: {str(e)}"
        )

@router.get("/{deck_id}/collaborators", response_model=List[DeckCollaborator])
def get_collaborators(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all collaborators for a deck"""
    try:
        # Check if deck exists
        deck = db.query(DeckModel).filter(DeckModel.id == deck_id).first()
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deck not found"
            )
        
        # Check if user has access to this deck
        if deck.owner_id != current_user.id:
            # Check if user is a collaborator
            collaborator = db.query(DeckCollaboratorModel).filter(
                DeckCollaboratorModel.deck_id == deck_id,
                DeckCollaboratorModel.user_id == current_user.id
            ).first()
            
            if not collaborator:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to access this deck"
                )
        
        collaborators = db.query(DeckCollaboratorModel).filter(
            DeckCollaboratorModel.deck_id == deck_id
        ).all()
        return collaborators
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching collaborators: {str(e)}"
        )