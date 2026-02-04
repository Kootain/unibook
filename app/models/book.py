from typing import List, Optional, Dict, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import JSON, Text
from uuid import uuid4
import time

if TYPE_CHECKING:
    from app.models.user import User

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
    user: Optional["User"] = Relationship(back_populates="books")
