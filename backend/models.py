from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import os
import sys

# Add the current directory to the path so we can import database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import Base
from passlib.context import CryptContext
import enum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    picture = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    decks = relationship("Deck", back_populates="owner")
    collaborations = relationship("DeckCollaborator", back_populates="user")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DeckVisibility(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"

class Deck(Base):
    __tablename__ = "decks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    visibility = Column(Enum(DeckVisibility), default=DeckVisibility.PRIVATE)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="decks")
    cards = relationship("Card", back_populates="deck")
    collaborators = relationship("DeckCollaborator", back_populates="deck")
    modules = relationship("Module", back_populates="deck", cascade="all, delete-orphan")

class Card(Base):
    __tablename__ = "cards"
    
    id = Column(Integer, primary_key=True, index=True)
    front_content = Column(Text)
    back_content = Column(Text)
    deck_id = Column(Integer, ForeignKey("decks.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    deck = relationship("Deck", back_populates="cards")

class DeckCollaborator(Base):
    __tablename__ = "deck_collaborators"
    
    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("decks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    deck = relationship("Deck", back_populates="collaborators")
    user = relationship("User", back_populates="collaborations")

class Module(Base):
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    deck_id = Column(Integer, ForeignKey("decks.id"))
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    deck = relationship("Deck", back_populates="modules")
    contents = relationship("ModuleContent", back_populates="module", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="module", cascade="all, delete-orphan")

class ContentItemType(str, enum.Enum):
    PDF = "pdf"
    YOUTUBE = "youtube"
    TEXT = "text"

class ModuleContent(Base):
    __tablename__ = "module_contents"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    content_type = Column(Enum(ContentItemType))
    content_data = Column(JSON)  # Store PDF path, YouTube URL, or text content
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    module = relationship("Module", back_populates="contents")

class QuestionType(str, enum.Enum):
    MCQ = "mcq"
    FILL_UP = "fill_up"
    FLASHCARD = "flashcard"
    MATCH_THE_FOLLOWING = "match_the_following"

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    question_type = Column(Enum(QuestionType))
    question_text = Column(Text)
    options = Column(JSON)  # Store options for MCQ, match pairs, etc.
    correct_answer = Column(JSON)  # Store correct answer(s)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    module = relationship("Module", back_populates="questions")