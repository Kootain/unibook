from typing import List, Optional, Dict, Any
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import JSON, Text
from uuid import UUID, uuid4
import datetime
import time

# Pydantic models for JSON fields (used for type validation)
class BookRequirement(SQLModel):
    topic: str
    targetAudience: str
    tone: str
    keyGoals: List[str]
    pageCountEstimate: int

class ChapterOutline(SQLModel):
    chapterNumber: int
    title: str
    description: str
    keyPoints: List[str]

class ChapterContent(SQLModel):
    chapterNumber: int
    title: str
    content: str
    reflection: str

# Database Models
class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    name: Optional[str] = None
    
    books: List["Book"] = Relationship(back_populates="user")

class Book(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    title: str
    coverImage: Optional[str] = Field(default=None, sa_column=Column(Text)) # Base64 string
    
    # Store complex objects as JSON
    # We use Dict/List[Dict] for the DB model to map to JSON column
    requirements: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    outline: List[Dict] = Field(default=[], sa_column=Column(JSON))
    chapters: List[Dict] = Field(default=[], sa_column=Column(JSON))
    
    createdAt: float = Field(default_factory=lambda: time.time() * 1000)
    status: str = Field(default="draft") # 'draft' | 'completed'
    
    user_id: Optional[str] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="books")

# API Models (DTOs)
class UserCreate(SQLModel):
    email: str
    password: str
    name: Optional[str] = None

class UserLogin(SQLModel):
    email: str
    password: str

class Token(SQLModel):
    token: str # Changed from access_token to match api_contract.ts "token"
    user: User # returning full user object as per contract

class AuthResponse(SQLModel):
    token: str
    user: User

# Book DTOs for API validation
class BookCreate(SQLModel):
    title: str
    coverImage: Optional[str] = None
    requirements: Optional[BookRequirement] = None
    outline: List[ChapterOutline] = []
    chapters: List[ChapterContent] = []
    status: str = "draft"

class BookUpdate(SQLModel):
    title: Optional[str] = None
    coverImage: Optional[str] = None
    requirements: Optional[BookRequirement] = None
    outline: List[ChapterOutline] = None
    chapters: List[ChapterContent] = None
    status: Optional[str] = None
