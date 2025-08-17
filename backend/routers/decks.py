from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from typing import List
from schemas import Deck, DeckCreate, DeckUpdate, Card, CardCreate, CardUpdate, DeckCollaborator, DeckCollaboratorCreate, Module, ModuleCreate, ModuleUpdate, ModuleContent, ModuleContentCreate, ModuleContentUpdate, Question, QuestionCreate, QuestionUpdate
from models import User, Deck as DeckModel, Card as CardModel, DeckCollaborator as DeckCollaboratorModel, Module as ModuleModel, ModuleContent as ModuleContentModel, Question as QuestionModel
from api_router import LoggingRoute
from auth_utils import get_user_by_email
from database import get_db
from config import SECRET_KEY, ALGORITHM
import jwt
from jwt.exceptions import InvalidTokenError
import os
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import magic

router = APIRouter(tags=["decks"])

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
        request.state.user = user
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
    card_update: CardUpdate,
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

# Module routes
@router.post("/{deck_id}/modules", response_model=Module)
def create_module(
    deck_id: int,
    module: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new module in a deck"""
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
                    detail="Not enough permissions to add modules to this deck"
                )
        
        db_module = ModuleModel(
            title=module.title,
            description=module.description,
            order=module.order,
            deck_id=deck_id
        )
        db.add(db_module)
        db.commit()
        db.refresh(db_module)
        
        # Create module contents if provided
        if module.contents:
            for content in module.contents:
                db_content = ModuleContentModel(
                    module_id=db_module.id,
                    content_type=content.content_type,
                    content_data=content.content_data,
                    order=content.order
                )
                db.add(db_content)
            db.commit()
        
        # Create questions if provided
        if module.questions:
            for question in module.questions:
                db_question = QuestionModel(
                    module_id=db_module.id,
                    question_type=question.question_type,
                    question_text=question.question_text,
                    options=question.options,
                    correct_answer=question.correct_answer,
                    order=question.order
                )
                db.add(db_question)
            db.commit()
        
        # Refresh to get the complete module with contents and questions
        db.refresh(db_module)
        return db_module
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating module: {str(e)}"
        )

@router.get("/{deck_id}/modules", response_model=List[Module])
def get_modules(
    deck_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all modules in a deck"""
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
        
        modules = db.query(ModuleModel).filter(
            ModuleModel.deck_id == deck_id
        ).offset(skip).limit(limit).all()
        return modules
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching modules: {str(e)}"
        )

@router.get("/{deck_id}/modules/{module_id}", response_model=Module)
def get_module(
    deck_id: int,
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific module by ID"""
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
        
        module = db.query(ModuleModel).filter(
            ModuleModel.id == module_id,
            ModuleModel.deck_id == deck_id
        ).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        return module
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching module: {str(e)}"
        )

@router.put("/{deck_id}/modules/{module_id}", response_model=Module)
def update_module(
    deck_id: int,
    module_id: int,
    module_update: ModuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a module"""
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
                    detail="Not enough permissions to update modules in this deck"
                )
        
        db_module = db.query(ModuleModel).filter(
            ModuleModel.id == module_id,
            ModuleModel.deck_id == deck_id
        ).first()
        
        if not db_module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # Update module fields
        update_data = module_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_module, field, value)
        
        db.commit()
        db.refresh(db_module)
        return db_module
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating module: {str(e)}"
        )

@router.delete("/{deck_id}/modules/{module_id}")
def delete_module(
    deck_id: int,
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a module"""
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
                    detail="Not enough permissions to delete modules from this deck"
                )
        
        db_module = db.query(ModuleModel).filter(
            ModuleModel.id == module_id,
            ModuleModel.deck_id == deck_id
        ).first()
        
        if not db_module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        db.delete(db_module)
        db.commit()
        return {"message": "Module deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting module: {str(e)}"
        )

# ModuleContent routes
@router.post("/{deck_id}/modules/{module_id}/contents", response_model=ModuleContent)
def create_module_content(
    deck_id: int,
    module_id: int,
    content: ModuleContentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new content item in a module"""
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
                    detail="Not enough permissions to add content to this module"
                )
        
        # Check if module exists and belongs to the deck
        module = db.query(ModuleModel).filter(
            ModuleModel.id == module_id,
            ModuleModel.deck_id == deck_id
        ).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        db_content = ModuleContentModel(
            module_id=module_id,
            content_type=content.content_type,
            content_data=content.content_data,
            order=content.order
        )
        db.add(db_content)
        db.commit()
        db.refresh(db_content)
        return db_content
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating module content: {str(e)}"
        )

@router.get("/{deck_id}/modules/{module_id}/contents", response_model=List[ModuleContent])
def get_module_contents(
    deck_id: int,
    module_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all content items in a module"""
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
        
        # Check if module exists and belongs to the deck
        module = db.query(ModuleModel).filter(
            ModuleModel.id == module_id,
            ModuleModel.deck_id == deck_id
        ).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        contents = db.query(ModuleContentModel).filter(
            ModuleContentModel.module_id == module_id
        ).offset(skip).limit(limit).all()
        return contents
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching module contents: {str(e)}"
        )

@router.put("/{deck_id}/modules/{module_id}/contents/{content_id}", response_model=ModuleContent)
def update_module_content(
    deck_id: int,
    module_id: int,
    content_id: int,
    content_update: ModuleContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a content item"""
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
                    detail="Not enough permissions to update content in this module"
                )
        
        # Check if module exists and belongs to the deck
        module = db.query(ModuleModel).filter(
            ModuleModel.id == module_id,
            ModuleModel.deck_id == deck_id
        ).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        db_content = db.query(ModuleContentModel).filter(
            ModuleContentModel.id == content_id,
            ModuleContentModel.module_id == module_id
        ).first()
        
        if not db_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content item not found"
            )
        
        # Update content fields
        update_data = content_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_content, field, value)
        
        db.commit()
        db.refresh(db_content)
        return db_content
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating module content: {str(e)}"
        )

@router.delete("/{deck_id}/modules/{module_id}/contents/{content_id}")
def delete_module_content(
    deck_id: int,
    module_id: int,
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a content item"""
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
                    detail="Not enough permissions to delete content from this module"
                )
        
        # Check if module exists and belongs to the deck
        module = db.query(ModuleModel).filter(
            ModuleModel.id == module_id,
            ModuleModel.deck_id == deck_id
        ).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        db_content = db.query(ModuleContentModel).filter(
            ModuleContentModel.id == content_id,
            ModuleContentModel.module_id == module_id
        ).first()
        
        if not db_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content item not found"
            )
        
        db.delete(db_content)
        db.commit()
        return {"message": "Content item deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting module content: {str(e)}"
        )

# Question routes
@router.post("/{deck_id}/modules/{module_id}/questions", response_model=Question)
def create_question(
    deck_id: int,
    module_id: int,
    question: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new question in a module"""
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
                    detail="Not enough permissions to add questions to this module"
                )
        
        # Check if module exists and belongs to the deck
        module = db.query(ModuleModel).filter(
            ModuleModel.id == module_id,
            ModuleModel.deck_id == deck_id
        ).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        db_question = QuestionModel(
            module_id=module_id,
            question_type=question.question_type,
            question_text=question.question_text,
            options=question.options,
            correct_answer=question.correct_answer,
            order=question.order
        )
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        return db_question
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating question: {str(e)}"
        )

@router.get("/{deck_id}/modules/{module_id}/questions", response_model=List[Question])
def get_questions(
    deck_id: int,
    module_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all questions in a module"""
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
        
        # Check if module exists and belongs to the deck
        module = db.query(ModuleModel).filter(
            ModuleModel.id == module_id,
            ModuleModel.deck_id == deck_id
        ).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        questions = db.query(QuestionModel).filter(
            QuestionModel.module_id == module_id
        ).offset(skip).limit(limit).all()
        return questions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching questions: {str(e)}"
        )

@router.put("/{deck_id}/modules/{module_id}/questions/{question_id}", response_model=Question)
def update_question(
    deck_id: int,
    module_id: int,
    question_id: int,
    question_update: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a question"""
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
                    detail="Not enough permissions to update questions in this module"
                )
        
        # Check if module exists and belongs to the deck
        module = db.query(ModuleModel).filter(
            ModuleModel.id == module_id,
            ModuleModel.deck_id == deck_id
        ).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        db_question = db.query(QuestionModel).filter(
            QuestionModel.id == question_id,
            QuestionModel.module_id == module_id
        ).first()
        
        if not db_question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Update question fields
        update_data = question_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_question, field, value)
        
        db.commit()
        db.refresh(db_question)
        return db_question
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating question: {str(e)}"
        )

@router.delete("/{deck_id}/modules/{module_id}/questions/{question_id}")
def delete_question(
    deck_id: int,
    module_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a question"""
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
                    detail="Not enough permissions to delete questions from this module"
                )
        
        # Check if module exists and belongs to the deck
        module = db.query(ModuleModel).filter(
            ModuleModel.id == module_id,
            ModuleModel.deck_id == deck_id
        ).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        db_question = db.query(QuestionModel).filter(
            QuestionModel.id == question_id,
            QuestionModel.module_id == module_id
        ).first()
        
        if not db_question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        db.delete(db_question)
        db.commit()
        return {"message": "Question deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting question: {str(e)}"
        )

# New endpoints for content management
@router.post("/{deck_id}/modules/{module_id}/contents/pdf", response_model=ModuleContent)
async def upload_pdf_content(
    deck_id: int,
    module_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a PDF file as content"""
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
                    detail="Not enough permissions to add content to this module"
                )
        
        # Check if module exists and belongs to the deck
        module = db.query(ModuleModel).filter(
            ModuleModel.id == module_id,
            ModuleModel.deck_id == deck_id
        ).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # Validate file type
        file_content = await file.read()
        file_type = magic.from_buffer(file_content, mime=True)
        if file_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed"
            )
        
        # Reset file pointer
        await file.seek(0)
        
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        import uuid
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Store file information in database
        content_data = {
            "filename": file.filename,
            "unique_filename": unique_filename,
            "file_path": file_path,
            "size": len(file_content),
            "content_type": "pdf"
        }
        
        db_content = ModuleContentModel(
            module_id=module_id,
            content_type="PDF",
            content_data=content_data,
            order=0  # Default order, can be updated later
        )
        db.add(db_content)
        db.commit()
        db.refresh(db_content)
        return db_content
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading PDF: {str(e)}"
        )

@router.post("/{deck_id}/modules/{module_id}/contents/text-to-pdf", response_model=ModuleContent)
async def convert_text_to_pdf(
    deck_id: int,
    module_id: int,
    text: str,
    title: str = "Generated PDF",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Convert text to PDF and save as content"""
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
                    detail="Not enough permissions to add content to this module"
                )
        
        # Check if module exists and belongs to the deck
        module = db.query(ModuleModel).filter(
            ModuleModel.id == module_id,
            ModuleModel.deck_id == deck_id
        ).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate PDF from text
        import uuid
        unique_filename = f"{uuid.uuid4()}_{title.replace(' ', '_')}.pdf"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Create PDF
        c = canvas.Canvas(file_path, pagesize=letter)
        c.setFont("Helvetica", 12)
        
        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, 750, title)
        
        # Add text content
        c.setFont("Helvetica", 12)
        text_object = c.beginText(72, 720)
        text_object.setTextOrigin(72, 720)
        
        # Split text into lines and add to PDF
        lines = text.split('\n')
        for line in lines:
            # Handle long lines by wrapping them
            if len(line) > 80:
                words = line.split(' ')
                current_line = ""
                for word in words:
                    if len(current_line + word) <= 80:
                        current_line += word + " "
                    else:
                        text_object.textLine(current_line)
                        current_line = word + " "
                text_object.textLine(current_line)
            else:
                text_object.textLine(line)
        
        c.drawText(text_object)
        c.save()
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Store file information in database
        content_data = {
            "text": text,
            "title": title,
            "filename": f"{title.replace(' ', '_')}.pdf",
            "unique_filename": unique_filename,
            "file_path": file_path,
            "size": file_size,
            "content_type": "text_to_pdf"
        }
        
        db_content = ModuleContentModel(
            module_id=module_id,
            content_type="PDF",
            content_data=content_data,
            order=0  # Default order, can be updated later
        )
        db.add(db_content)
        db.commit()
        db.refresh(db_content)
        return db_content
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error converting text to PDF: {str(e)}"
        )

def get_content_preview(content: ModuleContentModel):
    """Get preview for a content item"""
    content_type_upper = content.content_type.upper()
    print(content_type_upper,"aaaaaaaaaa")
    if content_type_upper == "TEXT":
        return {
            "content_type": "text",
            "preview": content.content_data[:500] + "..." if len(content.content_data) > 500 else content.content_data
        }
    elif content_type_upper == "PDF":
        return {
            "content_type": "pdf",
            "id": content.id,
            "metadata": content.content_data,
            "preview": f"PDF file: {content.content_data.get('filename', 'Unknown')}, Size: {content.content_data.get('size', 0)} bytes"
        }
    elif content_type_upper == "YOUTUBE":
        return {
            "content_type": "youtube",
            "url": content.content_data.get("url", ""),
            "preview": f"YouTube video: {content.content_data.get('url', '')}"
        }
    else:
        return {
            "content_type": "unknown",
            "preview": "Preview not available for this content type"
        }

@router.get("/{deck_id}/modules/{module_id}/contents/{content_id}/preview")
async def preview_module_content(
    deck_id: int,
    module_id: int,
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Preview content (for text content, return the text; for PDF, return metadata)"""
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
        
        # Check if module exists and belongs to the deck
        module = db.query(ModuleModel).filter(
            ModuleModel.id == module_id,
            ModuleModel.deck_id == deck_id
        ).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # Get the content with module relationship loaded
        content = db.query(ModuleContentModel).options(
            joinedload(ModuleContentModel.module)
        ).filter(
            ModuleContentModel.id == content_id,
            ModuleContentModel.module_id == module_id
        ).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Generate preview using the helper function
        return get_content_preview(content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error previewing content: {str(e)}"
        )

@router.get("/{deck_id}/modules/{module_id}/contents/{content_id}/pdf")
async def get_pdf_content(
    deck_id: int,
    module_id: int,
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Serve PDF content file"""
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
        
        # Check if module exists and belongs to the deck
        module = db.query(ModuleModel).filter(
            ModuleModel.id == module_id,
            ModuleModel.deck_id == deck_id
        ).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # Get the content
        content = db.query(ModuleContentModel).filter(
            ModuleContentModel.id == content_id,
            ModuleContentModel.module_id == module_id
        ).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Check if content is a PDF
        if content.content_type != "pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content is not a PDF file"
            )
        
        # Get file path from content data
        file_path = content.content_data.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF file not found"
            )
        
        # Return file response
        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=content.content_data.get("filename", "document.pdf")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error serving PDF content: {str(e)}"
        )