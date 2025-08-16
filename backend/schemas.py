from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserBase(BaseModel):
    email: str
    name: str
    picture: Optional[str] = None

class UserCreate(UserBase):
    google_id: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class DeckVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"

class CardBase(BaseModel):
    front_content: str
    back_content: str

class CardCreate(CardBase):
    pass

class Card(CardBase):
    id: int
    deck_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class DeckBase(BaseModel):
    title: str
    description: Optional[str] = None
    visibility: DeckVisibility = DeckVisibility.PRIVATE

class DeckCreate(DeckBase):
    pass

class DeckUpdate(DeckBase):
    pass

class Deck(DeckBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    cards: List[Card] = []
    
    class Config:
        orm_mode = True

class DeckCollaboratorBase(BaseModel):
    deck_id: int
    user_id: int

class DeckCollaboratorCreate(DeckCollaboratorBase):
    pass

class DeckCollaborator(DeckCollaboratorBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True