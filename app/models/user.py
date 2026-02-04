from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from uuid import uuid4
import datetime

if TYPE_CHECKING:
    from app.models.book import Book

class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    name: Optional[str] = None
    
    is_verified: bool = Field(default=False)
    verification_code: Optional[str] = None
    verification_expires: Optional[datetime.datetime] = None
    
    books: List["Book"] = Relationship(back_populates="user")
