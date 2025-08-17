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

class CardUpdate(BaseModel):
    front_content: Optional[str] = None
    back_content: Optional[str] = None

class Card(CardBase):
    id: int
    deck_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ContentItemType(str, Enum):
    PDF = "pdf"
    YOUTUBE = "youtube"
    TEXT = "text"

class ModuleContentBase(BaseModel):
    content_type: ContentItemType
    content_data: dict
    order: Optional[int] = 0

class ModuleContentCreate(ModuleContentBase):
    pass

class ModuleContentUpdate(BaseModel):
    content_type: Optional[ContentItemType] = None
    content_data: Optional[dict] = None
    order: Optional[int] = None

class ModuleContent(ModuleContentBase):
    id: int
    module_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class QuestionType(str, Enum):
    MCQ = "mcq"
    FILL_UP = "fill_up"
    FLASHCARD = "flashcard"
    MATCH_THE_FOLLOWING = "match_the_following"

class QuestionBase(BaseModel):
    question_type: QuestionType
    question_text: str
    options: Optional[dict] = None
    correct_answer: Optional[dict] = None
    order: Optional[int] = 0

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    question_type: Optional[QuestionType] = None
    question_text: Optional[str] = None
    options: Optional[dict] = None
    correct_answer: Optional[dict] = None
    order: Optional[int] = None

class Question(QuestionBase):
    id: int
    module_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class ModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: Optional[int] = 0

class ModuleCreate(ModuleBase):
    contents: Optional[List[ModuleContentCreate]] = []
    questions: Optional[List[QuestionCreate]] = []

class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None

class Module(ModuleBase):
    id: int
    deck_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    contents: List[ModuleContent] = []
    questions: List[Question] = []
    
    class Config:
        orm_mode = True

class DeckBase(BaseModel):
    title: str
    description: Optional[str] = None
    visibility: DeckVisibility = DeckVisibility.PRIVATE

class DeckCreate(DeckBase):
    pass

class DeckUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[DeckVisibility] = None

class Deck(DeckBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    cards: List[Card] = []
    modules: List['Module'] = []
    
    class Config:
        orm_mode = True

class DeckCollaboratorBase(BaseModel):
    deck_id: int
    user_id: int

class DeckCollaboratorCreate(BaseModel):
    user_id: int

class DeckCollaborator(DeckCollaboratorBase):
    id: int
    created_at: datetime
    user: User
    
    
    class Config:
        orm_mode = True